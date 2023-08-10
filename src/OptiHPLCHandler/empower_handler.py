import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .data_types import HplcResult, HPLCSetup, Sample
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
        sample_list: List[Sample],
        plate_list: List[Any],
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
            - OtherFields: List of other fields to add to the sample. Each field is a
                dictionary with the following keys:
                - name: Name of the field
                - value: Value of the field. Can be a string, number, or dictionary
                    with the following keys:
                    - member: Name of the member to use for the field
                    - value: Value of the member
            For all fields, the datatype will be autodetermined according the the type
                of the value. For Boolean
            values, this will errouneously be set to string. Instead, use
                `"value": {"member": “No”}` or `"value": {"member": “Yes”}`

        :param plate_list: List of plates to use. Each plate is a dictionary with the
            following keys:
            - plateTypeName: Name of the plate type
            - position: Position of the plate in the autosampler. This is what you
                reference in the sample value "SamplePos"

        :param audit_trail_message: Message to add to the audit trail of the sample set
            method
        """
        logger.debug("Posting experiment to Empower")
        sampleset_object = {"plates": plate_list, "name": sample_set_method_name}
        empower_sample_list = []
        for num, sample in enumerate(sample_list):
            logger.debug("Adding sample %s to sample list", sample["SampleName"])
            field_list = [
                {"name": "Function", "value": {"member": "Inject Samples"}},
                {"name": "Processing", "value": {"member": "Normal"}},
                {"name": "MethodSetOrReportMethod", "value": sample["Method"]},
                {"name": "Vial", "value": sample["SamplePos"]},
                {"name": "SampleName", "value": sample["SampleName"]},
                {"name": "InjVol", "value": sample["InjectionVolume"]},
            ]
            other_fields = sample.get("OtherFields", [])
            # Getting the other fields to add, or an empty list if no other fields are
            # given.
            for field in other_fields:
                logger.debug(
                    "adding field %s to sample %s", field["name"], sample["SampleName"]
                )
                field_list.append(field)
            for field in field_list:
                self._set_data_type(field)
            empower_sample_list.append(
                {"components": [], "id": num, "fields": field_list}
            )
        sampleset_object["sampleSetLines"] = empower_sample_list
        endpoint = "project/methods/sample-set-method"
        if audit_trail_message:
            logger.debug("Adding audit trail message to endpoint")
            endpoint += f"&auditTrailComment={audit_trail_message}"
        response = self.connection.post(endpoint=endpoint, body=sampleset_object)
        if response.status_code != 201:
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
        reply = self.connection.post(
            endpoint="acquisition/run-sample-set", body=parameters
        )
        if reply.status_code != 200:
            logger.error("Could not run experiment. Response: %s", reply.text)
            raise ValueError(f"Could not run experiment. Response: {reply.text}")

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
