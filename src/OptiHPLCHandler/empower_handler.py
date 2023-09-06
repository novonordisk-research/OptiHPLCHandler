import logging
from abc import ABC, abstractmethod
import warnings
from typing import Any, Dict, Generic, List, Optional, TypeVar

from requests.exceptions import HTTPError

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
    """
    Handler for Empower. It allows you to post experiments to Empower and run them. It
    also allows you to get the information necessary to create an experiment, that is,
    list of nodes, systems, plate types, and methods.

    This handler is stateful, meaning that you can save methods to the HPLC and run them
    later, and make runs based on the methods that are already on the HPLC.

    :attribute project: Name of the project to connect to.
    :attribute address: Address of the Empower server.
    :attribute username: Username to use to connect to Empower.
    """

    def __init__(
        self,
        project: str,
        address: str,
        service: str = None,
        allow_login_without_context_manager: bool = False,
        **kwargs,
    ):
        """
        Create a handler for Empower.

        :param project: Name of the project to connect to.
        :param address: Address of the Empower server.
        :param username: Username to use to connect to Empower. If not given, the
            username of the current user will be used.
        :param service: Name of the service to use to connect to Empower. If not given,
            the first service in the list of services will be used.
        :param password: Password to use to connect to Empower. If not given, the
            password will be retrieved from the keyring. If keyring is not available,
            the password will be asked for.
        """
        super().__init__(**kwargs)
        self.connection = EmpowerConnection(
            project=project,
            address=address,
            service=service,
        )
        self.allow_login_without_context_manager = allow_login_without_context_manager

    def __enter__(self):
        """Start the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """End the context manager."""
        self.__del__()

    def __del__(self):
        """Destructor for the EmpowerHandler."""
        try:
            self.connection.logout()
        except HTTPError as e:
            logger.warning("Error logging out of Empower: %s", e)
            warnings.warn("Error logging out of Empower: %s" % e)

    @property
    def project(self) -> str:
        return self.connection.project

    @property
    def address(self) -> str:
        return self.connection.address

    @property
    def username(self) -> str:
        return self.connection.username

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        has_context: bool = False,
    ):
        """
        Log into Empower.

        :param password: The password to use for logging in. If None, the password is
            retrieved from the keyring if available, otherwise it is asked for every
            time.
        :param username: The username to use for logging in. If None, the username of
            the default user is used. When EmpowerHandler is initialized, the
            username of the user running the script is set to the default username. If
            login is called with a different username, the default username is changed
            to the given username.
        """
        if not has_context:
            # If the login is not done in a context manager, it is only allowed if
            # `run_without_context` is True, and even there, it psots a warning.
            if self.allow_login_without_context_manager:
                logger.warning("Logging in without context.")
                warnings.warn(
                    "You are logging in manually without a context manager. "
                    "This is not recommended. "
                    "Please use a context manager, e.g. "
                    "`with EmpowerHandler(...) as handler:...`"
                )
            else:
                raise RuntimeError(
                    "Login without context is not allowed. "
                    "Please use a context manager, e.g. "
                    "`with EmpowerHandler(...) as handler:...`"
                )
        self.connection.login(password=password, username=username)

    def Status(self) -> List[HplcResult]:
        """Get the status of the HPLC."""
        raise NotImplementedError

    def PostExperiment(
        self,
        sample_set_method_name: str,
        sample_list: List[Dict[str, Any]],
        plates: Dict[str, str],
        audit_trail_message: Optional[str] = None,
    ):
        """
        Post the experiment to the HPLC.


        :param sample_set_method_name: Name of the sample set method to create.

        :param sample_list: List of samples to run. Each sample is a dictionary with
            the following keys:
            - Method: Name of the method to use for the sample.
            - SamplePos: Position of the sample in the autosampler, including plate and
                position on the plate.
            - SampleName: Name of the sample.
            - InjectionVolume: Volume of the sample to inject in micro liters.
            Any other keys will be added as fields to the sample, including custom
                fields.
            For all fields, the datatype will be autodetermined according the the type
                of the value.

        :param plate_list: Dict of plates to use. The keys should be the position of the
            plate, the value should be the plate type.

        :param audit_trail_message: Message to add to the audit trail of the sample set
            method.
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

        self.connection.post(endpoint=endpoint, body=sampleset_object)

    def RunExperiment(
        self,
        sample_set_method: str,
        node: str,
        system: str,  # TODO: Allow for none, in that case, use the only entry
        sample_set_name: Optional[str] = None,
    ) -> HplcResult:
        """
        Run the experiment on an instrument.

        :param sample_set_method: Name of the sample set method to run.
        :param node: Name of the node to run the experiment on.
        :param system: Name of the chromatographic system to run the experiment on.
        :param sample_set_name: Name of the sample set to run. If not given, the name
            of the sample set method will be used.
        """
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
            "systemName": system,
        }
        logger.debug("Running experiment with parameters %s", parameters)
        self.connection.post(
            endpoint="acquisition/run-sample-set-method", body=parameters
        )

    def AddMethod(
        self,
        template_method: str,
        new_method: str,
        changes: Dict[str, Any],
        audit_trail_message: str,
    ) -> None:
        """
        Add a new method based on the template method.

        :param template_method: Name of the template method to use.
        :param new_method: Name of the new method to create.
        :param changes: Dictionary of changes to make to the template method. The keys
            should be the names of the fields to change, the values should be the new
            values of the fields.
        :param audit_trail_message: Message to add to the audit trail of the method.
        """
        raise NotImplementedError

    def GetMethodList(self) -> List[str]:
        """Get the list of methods."""
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
        """Get the list of HPLC setups."""
        raise NotImplementedError

    def GetNodeNames(self) -> List[str]:
        """Get the list of node names."""
        response = self.connection.get(endpoint="acquisition/nodes")
        return response.json()["results"]

    def GetSystemNames(self, node: str) -> List[str]:
        """
        Get the list of names of chromatographic systems on a node.

        :param node: Name of the node to get the systems from.
        """
        endpoint = f"acquisition/chromatographic-systems?nodeName={node}"
        response = self.connection.get(endpoint=endpoint)
        return response.json()["results"]

    def GetSampleSetMethods(self) -> List[str]:
        """Get the list of sample set methods in project."""
        response = self.connection.get(
            endpoint="project/methods/sample-set-method-list"
        )
        return response.json()["results"]

    def GetPlateTypeNames(self, filter_string: Optional[None] = None) -> List[str]:
        """
        Get the list of names of available plate types

        :param filter_string: String to filter the list of plate types on. Only plate
            types whose name contains this string will be returned.
        """
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
