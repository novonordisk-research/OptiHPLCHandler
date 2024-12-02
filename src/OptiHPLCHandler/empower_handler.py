import logging
import warnings
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from .empower_api_core import EmpowerConnection
from .empower_instrument_method import EmpowerInstrumentMethod
from .utils.default_data import BUILTIN_ALLOWED_VALUES, RUN_MODES, SYNONYMS

logger = logging.getLogger(__name__)


class EmpowerHandler:
    """
    Handler for Empower. It allows you to post experiments to Empower and run them. It
    also allows you to get the information necessary to create an experiment, that is,
    list of nodes, systems, plate types, and methods.

    This handler is stateful, meaning that you can save methods to the HPLC and run them
    later, and make runs based on the methods that are already on the HPLC.

    :ivar project: Name of the project to connect to.
    :ivar address: Address of the Empower server.
    :ivar username: Username to use to connect to Empower.
    :ivar synonym_dict: Dictionary with the synonyms for the fields in SampleSetLine.
        The keys are the synonyms, the values are the actual field names that the API
        accepts.
    """

    def __init__(
        self,
        address: str,
        project: Optional[str] = None,
        service: str = None,
        username: Optional[str] = None,
        allow_login_without_context_manager: bool = False,
        auto_login: bool = True,
        **kwargs,
    ):
        """
        Create a handler for Empower.

        :param address: Address of the Empower server.
        :param project: Name of the project to connect to.
        :param service: Name of the service to use to connect to Empower. If not given,
            the first service in the list of services will be used.
        :param username: Username to use to connect to Empower. If not given, the name
            of the user running the script will be used.
        :param allow_login_without_context_manager: If `False` (default), an error will
            be raised when logging in without a context manager. If True, logging in
            without a context manager will merely raise a warning. This is not
            recommended, as it can lead to forgetting logging out.
        :param auto_login: If `True` (default), the handler will log in automatically
            when you start a context manager. If `False`, you will have to call
            `login()` manually. This will allow you to give the password manually.
        """
        super().__init__(**kwargs)
        self.connection = EmpowerConnection(
            project=project, address=address, service=service, username=username
        )
        self.allow_login_without_context_manager = allow_login_without_context_manager
        self.auto_login = auto_login
        self._has_context = False
        self._samplesetline_enum_dict = dict(BUILTIN_ALLOWED_VALUES)
        self.synonym_dict = dict(SYNONYMS)
        self.allowed_run_modes = RUN_MODES

    def __enter__(self):
        """Start the context manager."""
        self._has_context = True
        if self.auto_login:
            self.login()
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
        if not self._has_context:
            # If the login is not done in a context manager, it is only allowed if
            # `run_without_context` is True, and even there, it psots a warning.
            if self.allow_login_without_context_manager:
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
        # Setting the synonyms and enumerated fields.
        # Consider making this optional to save time if you know which enumerated
        # fields you are going to use.
        self.SetSynonymsAndEnumeratedFields()

    def SetSynonymsAndEnumeratedFields(self) -> None:
        """
        Set the synonyms and enumerated fields for SampleSetLines for the handler.

        The synonymes and enumerated fields are added to the ones that are already in
        the handler. Enumerated fileds are set to not be validated, as it takes a long
        time to get the values from the API. If you want to validate the values, you can
        set the values manually with `SetAllowedSamplesetLineFieldValues` by not giving
        the `allowed_values` parameter.
        """
        fields = self.connection.get("/project/fields?fieldType=SampleSetLine")[0]
        for field in fields:
            self.synonym_dict[field["displayName"]] = field["name"]
        enum_field_name_list = [
            field["name"] for field in fields if field["type"] == "Enumerator"
        ]
        for field_name in enum_field_name_list:
            self.SetAllowedSamplesetLineFieldValues(
                field_name=field_name, allowed_values=tuple(), overwrite=False
            )
            # Setting it to an empty tuple means that no validation is done if the
            # allowed values are not already set.

    def logout(self) -> None:
        """Log out of Empower."""
        logger.debug("Logging out of Empower")
        self.connection.logout()

    def GetEmpowerProjects(self) -> list[Dict[str, str]]:
        """
        Assuming that the user has logged in in one project for example
        project = Mobile, this method fetches all available projectName that
        the user has access to and returns them as a list.
        """
        project_list = self.connection.get("/authentication/project-list")[0]
        return project_list

    def PostExperiment(
        self,
        sample_set_method_name: str,
        sample_list: Iterable[dict[str, Any]],
        plates: Dict[str, str],
        audit_trail_message: Optional[str] = None,
        component_key: str = "Components",
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

            If the key "Components" is present, it should be a dict, with the keys being
            the names of the components, and the values being the concentration of the
            component in the sample.

            If you need to add a value to a custom field with the name "Components", you
            can change the name of the key to use for filling in the Empower components
            with the `component_key` parameter.

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
        plate_list = [
            {"plateTypeName": plate_name, "plateLayoutPosition": plate_pos}
            for plate_pos, plate_name in plates.items()
        ]
        sampleset_object = {"plates": plate_list, "name": sample_set_method_name}
        empower_sample_list = []
        for num, sample in enumerate(sample_list):
            if "Function" not in sample:
                sample["Function"] = "Inject Samples"
                if "Processing" not in sample:
                    sample["Processing"] = "Normal"
            logger.debug(
                "Adding sampleset line number %s to sample list",
                num,
            )
            component_list = []
            component_dict: dict[str, Union[str, float]] = sample.pop(component_key, {})
            # The key "Components" is treated differently, as Empower needs the
            # components separately, not as a field.
            for i, (component_name, component_value) in enumerate(
                component_dict.items()
            ):
                component_list.append(
                    {
                        "id": i,
                        "fields": [
                            {
                                "name": "Component",
                                "value": component_name,
                                "dataType": "String",
                            },
                            {
                                "name": "Value",
                                "value": component_value,
                                "dataType": "Double",
                            },
                        ],
                    }
                )
            field_list = []
            for key, value in sample.items():
                key = self.synonym_dict.get(key, key)
                # If you have logged in, the synonyms should be set, so this should not
                # be necessary, but we want to be able to use the handler by logging in
                # elsewhere.
                if key in self._samplesetline_enum_dict:
                    if isinstance(value, dict):
                        # If the value is a dict, it is already in the correct format.
                        # We will unpack it for the check, and then pack it again.
                        warnings.warn(
                            "You are using a dict as a value for an enumerated field. "
                            "This is deprecated and will be removed, "
                            "please use the value directly.",
                            DeprecationWarning,
                        )
                        value = value["member"]
                    if (
                        len(self._samplesetline_enum_dict[key])
                        != 0  # Empty tuple means no validation
                        and value not in self._samplesetline_enum_dict[key]
                    ):
                        raise ValueError(
                            f"Value {value} not in enumerated values for field {key}. "
                            f"Available values: {self._samplesetline_enum_dict[key]}"
                        )
                    value = {"member": value}
                logger.debug("Adding field %s with value %s to sample.", key, value)
                field_list.append(self._set_data_type({"name": key, "value": value}))
            empower_sample_list.append(
                {"components": component_list, "id": num, "fields": field_list}
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
        run_mode: str = "RunOnly",
    ) -> None:
        """
        Run the experiment on an instrument.

        :param sample_set_method: Name of the sample set method to run.
        :param node: Name of the node to run the experiment on.
        :param system: Name of the chromatographic system to run the experiment on.
        :param sample_set_name: Name of the sample set to run. If not given, the name
            of the sample set method will be used.
        :param run_mode: The run mode. Must be one of "RunOnly", "RunAndProcess", or
            "RunAndReport".
        """
        if run_mode not in self.allowed_run_modes:
            raise ValueError(
                f"Run mode {run_mode} not in "
                f"available run modes: {self.allowed_run_modes}."
            )
        parameters = {
            "sampleSetMethodName": sample_set_method,
            "sampleSetName": sample_set_name,
            "shutDownMethodName": "",
            "processingPrinter": "",
            "runMode": run_mode,
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
        ).content
        method_name_dict_list = [
            [name_dict for name_dict in method["fields"] if name_dict["name"] == "Name"]
            for method in method_list
        ]
        if any(len(name_dict) > 1 for name_dict in method_name_dict_list):
            raise ValueError("Multiple names found for a method.")
        if any(len(name_dict) == 0 for name_dict in method_name_dict_list):
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
        if self.connection.api_version == "1.0":
            return EmpowerInstrumentMethod(response.content[0], use_sample_manager_oven)
        return EmpowerInstrumentMethod(response.content, use_sample_manager_oven)

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
        if self.connection.api_version == "1.0":
            return response.content[0]
        return response.content

    def PostMethodSetMethod(self, method: Mapping[str, Any]) -> None:
        """
        Post a method set method.

        :param method: The method set method to post."""
        endpoint = "project/methods/method-set"
        self.connection.post(endpoint=endpoint, body=method)

    def GetNodeNames(self) -> List[str]:
        """Get the list of node names."""
        return self.connection.get(endpoint="acquisition/nodes").content

    def GetSystemNames(self, node: str) -> List[str]:
        """
        Get the list of names of chromatographic systems on a node.

        :param node: Name of the node to get the systems from.
        """
        endpoint = f"acquisition/chromatographic-systems?nodeName={node}"
        return self.connection.get(endpoint=endpoint).content

    def GetSampleSetMethods(self) -> List[str]:
        """Get the list of sample set methods in project."""
        return self.connection.get(
            endpoint="project/methods/sample-set-method-list"
        ).content

    def GetPlateTypeNames(self, filter_string: Optional[str] = None) -> List[str]:
        """
        Get the list of names of available plate types

        :param filter_string: String to filter the list of plate types on. Only plate
            types whose name contains this string will be returned.
        """
        endpoint = "configuration/plate-types-list"
        if filter_string:
            endpoint += f"?stringFilter={filter_string}"
        return self.connection.get(endpoint=endpoint).content

    def GetStatus(self, node: str, system: str):
        endpoint = (
            "acquisition/chromatographic-system-status"
            f"?nodeName={node}&systemName={system}"
        )
        result_list = self.connection.get(endpoint=endpoint, timeout=120).content
        return {entry["name"]: entry["value"] for entry in result_list}

    def SetAllowedSamplesetLineFieldValues(
        self,
        field_name: str,
        allowed_values: Optional[List[str]] = None,
        overwrite: bool = True,
    ) -> List[str]:
        """
        Set the list of allowed values for a field in SampleSetLine.

        :param field_name: Name of the field to set the allowed values for. Can be
            either the actual field name or an excepted synonym, like the Empower
            display name.
        :param allowed_values: List of values to set as enumerated values for the field.
            If None (default), the list of enumerated values will be retrieved from the
            API. To turn off validation for a field, set the values to an empty tuple.
        :param overwrite: If True (default), the allowed values for the field will be
            overwritten, even if they are already set. If False, the values will only
            be set if they are not already set.

        :return: List of allowed values for the field after the operation.
        """
        field_name = self.synonym_dict.get(field_name, field_name)
        if field_name not in self._samplesetline_enum_dict:
            logger.debug("Field %s not in enum_dict, adding it.", field_name)
        elif not overwrite:
            logger.debug(
                "Allowed values for field %s already set (%s). "
                "These will not be overwritten.",
                field_name,
                self._samplesetline_enum_dict[field_name],
            )
            return self._samplesetline_enum_dict[field_name]
        elif self._samplesetline_enum_dict[field_name] != tuple():
            logger.debug(
                "Allowed values for field %s already set (%s). "
                "These will be overwritten with %s.",
                field_name,
                self._samplesetline_enum_dict[field_name],
                allowed_values,
            )
        if allowed_values is None:
            fields = self.connection.get(
                "/project/field-enumerated-values"
                "?fieldType=SampleSetLine"
                f"&field={field_name}"
            )[0]
            allowed_values = [field["member"] for field in fields]
        self._samplesetline_enum_dict[field_name] = allowed_values
        return allowed_values

    @classmethod
    def LogoutAllSessions(
        cls,
        address: str,
        password: str,
        service: Optional[str] = None,
        username: Optional[str] = None,
    ):
        """
        Logout all sessions of the user.

        :param project: Name of the project to connect to.
        :param address: Address of the Empower server.
        :param password: Password to use to connect to Empower.
        :param service: Name of the service to use to connect to Empower. If not given,
            the first service in the list of services will be used.
        :param username: Username to use to connect to Empower.
        """
        handler = cls(
            address=address, service=service, username=username, auto_login=False
        )
        with handler:
            handler.login(password=password)
            session_list = handler.connection.get(
                endpoint="authentication/session-infoes", timeout=120
            )[0]
            session_list = [
                session
                for session in session_list
                if session["user"] == handler.username
            ]
            # Only keeping the session IDs of the current user.
            session_list = [
                session
                for session in session_list
                if session["id"] != handler.connection.session_id
            ]
            # Removing the session in handler, so we don't log out of that before we are
            # done. It is logged out when we exit the context manager.
            connection = EmpowerConnection(
                address=address,
                username=handler.username,
                service=handler.connection.service,
            )
            for session in session_list:
                connection.token = handler.connection.token
                # The token doesn't have to be from the same session, so we can use the
                # token from the handler.
                connection.session_id = session["id"]
                logger.debug("Logging out of session %s", session["id"])
                connection.logout()

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
            raise ValueError(
                "No data type found for field "
                f"{field['name']} with value {field['value']}."
            )
        return field

    def __str__(self):
        return f"EmpowerHandler for project {self.project}, user {self.username}"
