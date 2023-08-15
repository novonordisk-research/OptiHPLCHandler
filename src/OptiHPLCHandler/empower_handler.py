import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .data_types import HplcResult, HPLCSetup
from .empower_api_core import EmpowerConnection

Result = TypeVar("Result")

Setup = TypeVar("Setup")

logger = logging.getLogger(__name__)


class StatefulInstrumentHandler(ABC, Generic[Result, Setup]):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def Status(self) -> List[Result]:
        pass

    @abstractmethod
    def PostExperiment(experiment: Any):
        """
        Post the experiment to the instrument.
        """
        pass

    @abstractmethod
    def RunExperiment(experiment: Any) -> Result:
        """
        Run the experiment on the instrument.

        This will run an experiment that already exists .
        """
        pass

    @abstractmethod
    def GetSetup() -> List[Setup]:
        pass


class EmpowerHandler(StatefulInstrumentHandler[HplcResult, HPLCSetup]):
    def __init__(
        self,
        project: str,
        address: str,
        username: Optional[str] = None,
        service: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.connection = EmpowerConnection(
            project=project, address=address, username=username, service=service
        )

    @property
    def project(self) -> str:
        return self.connection.project

    @property
    def address(self) -> str:
        return self.connection.address

    @property
    def username(self) -> str:
        return self.connection.username

    def Status(self) -> List[HplcResult]:
        """Get the status of the HPLC."""
        raise NotImplementedError

    def PostExperiment(
        self,
        sample_set_method_name: str,
        sample_list: List[Dict[str, Any]],
        plates: Dict[str, str],
        audit_trail_message: str,
    ):
        """
        Post the experiment to the HPLC.


        :param sample_set_method_name: Name of the sample set method. This will be the
            name of the sample set in Empower.

        :param sample_list: List of samples to run. Each sample is a dictionary with
            the following keys:
            - Method: Name of the method to use for the sample
            - SamplePos: Position of the sample in the autosampler, including plate and
                position on the plate
            - SampleName: Name of the sample
            - InjectionVolume: Volume of the sample to inject in micro liters
            Any other keys will be added as fields to the sample, including custom
                fields.
            For all fields, the datatype will be autodetermined according the the type
                of the value.

        :param plate_list: Dict of plates to use. The keys should be the position of the
            plate, the value should be the plate type.

        :param audit_trail_message: Message to add to the audit trail of the sample set
            method
        """
        logger.debug("Posting experiment to Empower")
        plate_list = []
        for plate_pos, plate_name in plates.items():
            plate_list.append(
                {
                    "plateTypeName": plate_name,
                    "plateLayoutPosition": plate_pos,
                }
            )
        sampleset_object = {"plates": plate_list, "name": sample_set_method_name}
        empower_sample_list = []
        for num, sample in enumerate(sample_list):
            logger.debug(
                "Adding sample number %s with name %s to sample list",
                num,
                sample["SampleName"],
            )
            alias_dict = {
                "Method": "MethodSetOrReportMethod",
                "SamplePos": "Vial",
                "InjectionVolume": "InjVol",
            }  # Key are "human readable" names, values are the names used in Empower.
            field_list = [
                {"name": "Function", "value": {"member": "Inject Samples"}},
                {"name": "Processing", "value": {"member": "Normal"}},
            ]
            for key, value in sample.items():
                if key in alias_dict:
                    key = alias_dict[key]
                logger.debug("Adding field %s with value %s to sample.", key, value)
                field_list.append({"name": key, "value": value})
            for field in field_list:
                self._set_data_type(field)
            empower_sample_list.append(
                {"components": [], "id": num, "fields": field_list}
            )
        sampleset_object["sampleSetLines"] = empower_sample_list
        endpoint = "project/methods/sample-set-method"
        if audit_trail_message:
            logger.debug("Adding audit trail message to endpoint")
            endpoint += f"?auditTrailComment={audit_trail_message}"
        response = self.connection.post(endpoint=endpoint, body=sampleset_object)
        if response.status_code != 201:
            if response.status_code == 404:
                logger.error("Could not post sample set method. Resource not found.")
                raise ValueError(
                    "Could not post sample set method. Resource not found."
                )
            logger.error(
                "Could not post sample set method. Response: %s", response.text
            )
            raise ValueError(
                f"Could not post sample set method. Response: {response.text}"
            )

    def RunExperiment(
        self,
        sample_set_method: str,
        node: str,
        hplc: str = None,
        sample_set_name: Optional[str] = None,
    ) -> HplcResult:
        """Run the experiment on an instrument."""
        parameters = {
            "sampleSetMethodName": sample_set_method,
            "sampleSetName": sample_set_name,
            "shutDownMethodName": "",
            "processingPrinter": "",
            "runMode": "RunOnly",
            "suitabilityMode": "ContinueOnFault",
            "waitForUser": False,
            "reRun": False,
            "sampleSetId": 0,
            "fromLine": 0,
            "nodeName": node,
            "systemName": hplc,
        }
        logger.debug("Running experiment with parameters %s", parameters)
        response = self.connection.post(
            endpoint="acquisition/run-sample-set-method", body=parameters
        )
        if response.status_code != 200:
            if response.status_code == 404:
                logger.error("Could not post sample set method. Resource not found.")
                raise ValueError(
                    "Could not post sample set method. Resource not found."
                )
            logger.error(
                "Could not post sample set method. Response: %s", response.text
            )
            raise ValueError(
                f"Could not post sample set method. Response: {response.text}"
            )

    def AddMethod(
        self,
        template_method: str,
        new_method: str,
        changes: Dict[str, Any],
        audit_trail_message: str,
    ) -> None:
        """Add a new method based on the template method."""
        raise NotImplementedError

    def GetMethodList(self) -> List[str]:
        """Get the list of methods"""
        response = self.connection.get(
            endpoint="project/methods?methodTypes=MethodSetMethod"
        )
        method_name_dict_list = [
            [name_dict for name_dict in method["fields"] if name_dict["name"] == "Name"]
            for method in response.json()["results"]
        ]
        if any([len(name_dict) > 1 for name_dict in method_name_dict_list]):
            logger.error("Multiple names found for a method.")
            raise ValueError("Multiple names found for a method.")
        if any([len(name_dict) == 0 for name_dict in method_name_dict_list]):
            logger.error("No name found for a method.")
            raise ValueError("No name found for a method.")
        method_name_list = [
            name_dict[0]["value"] for name_dict in method_name_dict_list
        ]
        logger.debug("Found methods %s", method_name_list)
        return method_name_list

    def GetSetup(self) -> List[HPLCSetup]:
        """Get the list of HPLC setups"""
        raise NotImplementedError
    
    def GetNodeNames(self) -> List[str]:
        """Get the list of node names"""
        response = self.connection.get(endpoint="acquisition/nodes")
        return response.json()["results"]
    
    def GetSystemNames(self, node: str) -> List[str]:
        """Get the list of names of chromatographic systems on a node"""
        endpoint = f"acquisition/chromatographic-systems?nodeName={node}"
        response = self.connection.get(endpoint=endpoint)
        return response.json()["results"]

    def GetPlateTypeNames(self, filter_string: Optional[None] = None) -> List[str]:
        """Get the list of names of available plate types"""
        endpoint = "configuration/plate-types-list"
        if filter_string:
            endpoint += f"?stringFilter={filter_string}"
        response = self.connection.get(endpoint=endpoint)
        return response.json()["results"]

    def _set_data_type(self, field: Dict[str, Any]):
        """Find and set the data type of the field, based on the type of `value"""
        data_type_dict = {
            str: "String",
            int: "Double",
            float: "Double",
            dict: "Enumerator",
        }
        data_type = type(field["value"])
        logger.debug("Setting data type of field %s to %s", field["name"], data_type)
        field["dataType"] = data_type_dict[data_type]
