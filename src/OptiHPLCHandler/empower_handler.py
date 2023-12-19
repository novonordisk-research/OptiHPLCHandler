import logging
import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Iterable, List, Mapping, Optional, TypeVar

from .data_types import HplcResult, HPLCSetup
from .empower_api_core import EmpowerConnection
from .empower_instrument_method import EmpowerInstrumentMethod

Result = TypeVar("Result")

Setup = TypeVar("Setup")

logger = logging.getLogger(__name__)


class StatefulInstrumentHandler(ABC, Generic[Result, Setup]):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def Status(self) -> List[Result]:
        """Get the status of the instrument."""

    @abstractmethod
    def PostExperiment(self, experiment: Any):
        """
        Post the experiment to the instrument.
        """

    @abstractmethod
    def RunExperiment(self, experiment: Any) -> Result:
        """
        Run the experiment on the instrument.

        This will run an experiment that already exists .
        """

    @abstractmethod
    def GetSetup(self) -> List[Setup]:
        """Get the setup of the instrument."""


class EmpowerHandler(StatefulInstrumentHandler[HplcResult, HPLCSetup]):
    """
    Handler for Empower. It allows you to post experiments to Empower and run them. It
    also allows you to get the information necessary to create an experiment, that is,
    list of nodes, systems, plate types, and methods.

    This handler is stateful, meaning that you can save methods to the HPLC and run them
    later, and make runs based on the methods that are already on the HPLC.

    :ivar project: Name of the project to connect to.
    :ivar address: Address of the Empower server.
    :ivar username: Username to use to connect to Empower.
    """

    def __init__(
        self,
        project: str,
        address: str,
        service: str = None,
        username: Optional[str] = None,
        allow_login_without_context_manager: bool = False,
        auto_login: bool = True,
        **kwargs,
    ):
        """
        Create a handler for Empower.

        :param project: Name of the project to connect to.
        :param address: Address of the Empower server.
        :param service: Name of the service to use to connect to Empower. If not given,
            the first service in the list of services will be used.
        :param allow_login_without_context_manager: If `False` (default), an error will
            be raised when logging in without a context manager. If True, logging in
            without a context manager will merely raise a warning. This is not
            recommended, as it can lead to forgetting logging out.
        :param auto_login: If True (default), the handler will log in automatically when
            you start a context manager. If `False`, you will have to call `login`
            manually. If you are to provide the password, you need to set this to
            `False`.
        """
        super().__init__(**kwargs)
        self.connection = EmpowerConnection(
            project=project,
            address=address,
            service=service,
        )
        self.allow_login_without_context_manager = allow_login_without_context_manager
        self.auto_login = auto_login
        self._has_context = False
        if username:
            self.username = username

    def __enter__(self):
        """Start the context manager."""
        if self.auto_login:
            self.login(has_context=True)
        self._has_context = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """End the context manager."""
        self._has_context = False
        self.logout()

    @property
    def project(self) -> str:
        """Get the Empower project name."""
        return self.connection.project

    @project.setter
    def project(self, project: str) -> None:
        self.connection.project = project

    @property
    def address(self) -> str:
        """Get the URL for the Empower Web API to connect to."""
        return self.connection.address

    # Changing the address would require a new lookup for the service, so it is not
    # allowed.

    @property
    def username(self) -> str:
        return self.connection.username

    @username.setter
    def username(self, username: str) -> None:
        self.connection.username = username

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
                    "This is not recommended.\n"
                    "Please use a context manager, e.g.\n"
                    "`with EmpowerHandler(...) as handler:...`"
                )
            else:
                raise RuntimeError(
                    "Login without context is not allowed. "
                    "Please use a context manager, e.g. "
                    "`with EmpowerHandler(...) as handler:...`"
                )
        self.connection.login(password=password, username=username)

    def logout(self) -> None:
        """Log out of Empower."""
        logger.debug("Logging out of Empower")
        self.connection.logout()

    @property
    def Status(self) -> List[HplcResult]:
        """Get the status of the HPLC."""
        raise NotImplementedError

    def PostExperiment(
        self,
        sample_set_method_name: str,
        sample_list: Iterable[Mapping[str, Any]],
        plates: Dict[str, str],
        audit_trail_message: Optional[str] = None,
    ):
        """
        Post the experiment to the HPLC.

        :param sample_set_method_name: Name of the sample set method to create.
        :param sample_list: List of samples to run. Each sample is a dictionary with
            the following keys:
                - Method: Name of the method to use for the sample.
                - SamplePos: Position of the sample in the autosampler, including plate
                    and position on the plate.
                - SampleName: Name of the sample.
                - InjectionVolume: Volume of the sample to inject in micro liters.

            Any other keys will be added as fields to the sample, including custom
            fields.
            If the key Function does not exist, the Function is set to "Inject Sample"
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
            if "Function" not in sample:
                sample["Function"] = {"member": "Inject Samples"}
                field_list = [
                    {"name": "Processing", "value": {"member": "Normal"}},
                ]
            else:
                field_list = []
            logger.debug(
                "Adding sampleset line number %s to sample list",
                num,
            )
            alias_dict = {
                "Method": "MethodSetOrReportMethod",
                "SamplePos": "Vial",
                "InjectionVolume": "InjVol",
            }  # Key are "human readable" names, values are the names used in Empower.
            for key, value in sample.items():
                key = alias_dict.get(key, key)
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
            endpoint="acquisition/run-sample-set-method", body=parameters, timeout=60
        )

    def AddMethod(
        self,
        template_method: str,
        new_method: str,
        changes: Mapping[str, Any],
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

    def GetMethodList(self, method_type: str = "MethodSetMethod") -> List[str]:
        """
        Get the list of methods.

        :param method_type: Type of methods to get. If it doesn't end with "Method", it
            will be added. Default: "MethodSetMethod".
        """
        if not method_type.endswith("Method"):
            method_type += "Method"
        method_list = self.connection.get(
            endpoint="project/methods?methodTypes=" + method_type
        )[0]
        method_name_dict_list = [
            [name_dict for name_dict in method["fields"] if name_dict["name"] == "Name"]
            for method in method_list
        ]
        if any(len(name_dict) > 1 for name_dict in method_name_dict_list):
            logger.error("Multiple names found for a method.")
            raise ValueError("Multiple names found for a method.")
        if any(len(name_dict) == 0 for name_dict in method_name_dict_list):
            logger.error("No name found for a method.")
            raise ValueError("No name found for a method.")
        method_name_list = [
            name_dict[0]["value"] for name_dict in method_name_dict_list
        ]
        logger.debug("Found methods %s", method_name_list)
        return method_name_list

    def GetInstrumentMethod(
        self, method_name: str, use_sample_manager_oven: bool = False
    ) -> EmpowerInstrumentMethod:
        """
        Get a method set method.

        :param method_name: Name of the method set method to get.
        :param use_sample_manager_oven: If True, both sample manager oven and column
            manager oven will be used. If False, only column manager oven will be used.
        """
        response = self.connection.get(
            endpoint=f"project/methods/instrument-method?name={method_name}"
        )
        return EmpowerInstrumentMethod(response[0][0], use_sample_manager_oven)

    def PostInstrumentMethod(self, method: EmpowerInstrumentMethod) -> None:
        """
        Post a method set method to Empower.

        :param method: The method set method to post."""
        endpoint = "project/methods/instrument-method?overWriteExisting=false"
        self.connection.post(endpoint=endpoint, body=method.current_method)

    def GetMethodSetMethod(self, method_name: str):
        """
        Get a method set method.

        :param method_name: Name of the method set method to get.
        """
        response = self.connection.get(
            endpoint=f"project/methods/method-set?name={method_name}"
        )
        return response[0][0]

    def PostMethodSetMethod(self, method: Mapping[str, Any]) -> None:
        """
        Post a method set method.

        :param method: The method set method to post."""
        endpoint = "project/methods/method-set"
        self.connection.post(endpoint=endpoint, body=method)

    def GetSetup(self) -> List[HPLCSetup]:
        """Get the list of HPLC setups."""
        raise NotImplementedError

    def GetNodeNames(self) -> List[str]:
        """Get the list of node names."""
        return self.connection.get(endpoint="acquisition/nodes")[0]

    def GetSystemNames(self, node: str) -> List[str]:
        """
        Get the list of names of chromatographic systems on a node.

        :param node: Name of the node to get the systems from.
        """
        endpoint = f"acquisition/chromatographic-systems?nodeName={node}"
        return self.connection.get(endpoint=endpoint)[0]

    def GetSampleSetMethods(self) -> List[str]:
        """Get the list of sample set methods in project."""
        return self.connection.get(endpoint="project/methods/sample-set-method-list")[0]

    def GetPlateTypeNames(self, filter_string: Optional[str] = None) -> List[str]:
        """
        Get the list of names of available plate types

        :param filter_string: String to filter the list of plate types on. Only plate
            types whose name contains this string will be returned.
        """
        endpoint = "configuration/plate-types-list"
        if filter_string:
            endpoint += f"?stringFilter={filter_string}"
        return self.connection.get(endpoint=endpoint)[0]

    def GetStatus(self, node: str, system: str):
        endpoint = (
            "acquisition/chromatographic-system-status"
            f"?nodeName={node}&systemName={system}"
        )
        result_list = self.connection.get(endpoint=endpoint, timeout=120)[0]
        return {entry["name"]: entry["value"] for entry in result_list}

    def _set_data_type(self, field: Mapping[str, Any]):
        """Find and set the data type of the field, based on the type of `value`"""
        data_type_dict = {
            str: "String",
            int: "Double",
            float: "Double",
            dict: "Enumerator",
        }
        for key, value in data_type_dict.items():
            if isinstance(field["value"], key):
                logger.debug(
                    "Setting data type of field %s to %s.", field["name"], value
                )
                field["dataType"] = value
        if "dataType" not in field:
            message = (
                "No data type found for field "
                f"{field['name']} with value {field['value']}."
            )
            logger.error(message)
            raise ValueError(message)

    def __str__(self):
        return f"EmpowerHandler for project {self.project}, user {self.username}"
