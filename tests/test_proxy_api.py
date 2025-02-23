import unittest
from unittest.mock import MagicMock, patch

from OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod, EmpowerModuleMethod
from OptiHPLCHandler.empower_api_core import EmpowerResponse


def create_empower_response(content):
    return EmpowerResponse(content, "", True, False)


class TestEmpowerHandler(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, mock_connection) -> None:
        mock_response = MagicMock()
        mock_response.address = "https://test_address"
        mock_response.username = "test_username"
        mock_response.project = "test_project"
        mock_response.token = None
        mock_connection.return_value = mock_response

        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_initialisation(self):
        assert self.handler.project == "test_project"
        assert self.handler.username == "test_username"
        assert self.handler.address == "https://test_address"
        assert self.handler.auto_login is True
        # Check that the trailing slash is removed from the address

    def test_run_experiment(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.handler.connection.post.return_value = mock_response
        self.handler.RunExperiment(
            sample_set_method="test_sample_set_method",
            node="test_node",
            system="test_hplc",
        )
        assert (
            self.handler.connection.post.call_args[1]["endpoint"]
            == "acquisition/run-sample-set-method"
        )  # Check that the correct URl is used.
        assert (
            self.handler.connection.post.call_args[1]["body"]["sampleSetMethodName"]
        ) == "test_sample_set_method"
        # Check that the correct sample set method is used.
        assert (
            self.handler.connection.post.call_args[1]["body"]["nodeName"]
        ) == "test_node"  # Check that the correct node is used.
        assert (
            self.handler.connection.post.call_args[1]["body"]["systemName"]
        ) == "test_hplc"  # Check that the correct HPLC is used.
        assert (
            self.handler.connection.post.call_args[1]["body"]["sampleSetName"]
        ) is None  # Check that no sample set name is given
        self.handler.RunExperiment(
            sample_set_method="test_sample_set_method",
            node="test_node",
            system="test_hplc",
            sample_set_name="test_sample_set_name",
        )
        assert (
            self.handler.connection.post.call_args[1]["body"]["sampleSetName"]
        ) == "test_sample_set_name"  # Check that the correct sample set name is given

    def test_explicit_run_mode(self):
        self.handler.RunExperiment(
            sample_set_method="test_sample_set_method",
            node="test_node",
            system="test_hplc",
            run_mode="RunAndReport",
        )
        assert (self.handler.connection.post.call_args[1]["body"]["runMode"]) == (
            "RunAndReport"
        )

    def test_invalid_run_mode(self):
        with self.assertRaises(ValueError):
            self.handler.RunExperiment(
                sample_set_method="test_sample_set_method",
                node="test_node",
                system="test_hplc",
                run_mode="InvalidRunMode",
            )

    def test_get_node_name_list(self):
        self.handler.connection.get.return_value = create_empower_response(
            ["test_node_name_1"]
        )
        node_name_list = self.handler.GetNodeNames()
        assert node_name_list == ["test_node_name_1"]
        assert (
            "acquisition/nodes" in self.handler.connection.get.call_args[1]["endpoint"]
        )

    def test_get_system_name_list(self):
        self.handler.connection.get.return_value = create_empower_response(
            ["test_system_name_1"]
        )
        system_name_list = self.handler.GetSystemNames("test_node_name")
        assert system_name_list == ["test_system_name_1"]
        assert (
            "acquisition/chromatographic-systems?nodeName=test_node_name"
            == self.handler.connection.get.call_args[1]["endpoint"]
        )

    def test_get_empower_projects(self):
        self.handler.connection.get.return_value = (
            [
                {"projectName": "2023\\RP0649", "shortName": "RP0649"},
                {"projectName": "2023\\RP0650", "shortName": "RP0650"},
            ],
            "N/A",
        )

        empower_projects_list = self.handler.GetEmpowerProjects()
        assert isinstance(empower_projects_list, list)
        assert isinstance(empower_projects_list[0], dict)
        assert "projectName" in empower_projects_list[0]
        assert "shortName" in empower_projects_list[0]
        assert empower_projects_list[0]["projectName"] == "2023\\RP0649"
        assert empower_projects_list[0]["shortName"] == "RP0649"
        assert empower_projects_list[1]["projectName"] == "2023\\RP0650"
        assert empower_projects_list[1]["shortName"] == "RP0650"

    def test_project_setter(self):
        self.handler.project = "test_project"
        assert self.handler.connection.project == "test_project"

    def test_address_setter(self):
        # Changing the address would require a new lookup for the service, so it is not
        # allowed.
        with self.assertRaises(AttributeError):
            self.handler.address = "test_address"


class TestSampleList(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_post_sample_list(self):
        sample_list = [
            {
                "Method": "test_method_1",
                "SamplePos": "test_sample_pos_1",
                "SampleName": "test_sample_name_1",
                "InjectionVolume": 1,
            },
            {
                "Method": "test_method_2",
                "SamplePos": "test_sample_pos_2",
                "SampleName": "test_sample_name_2",
                "InjectionVolume": 2,
                "test_field_1": "test_value",
                "test_field_2": 2.3,
            },
        ]
        self.handler.PostExperiment(
            sample_set_method_name="test_sampleset_name",
            sample_list=sample_list,
            plates={},
            audit_trail_message="test_audit_trail_message",
        )
        assert (
            "test_sampleset_name"
            == self.handler.connection.post.call_args[1]["body"]["name"]
        )
        # Testing that the name is correct in the request
        assert (
            "?auditTrailComment=test_audit_trail_message"
            in self.handler.connection.post.call_args[1]["endpoint"]
        )
        # Testing that the audit trail message is correct
        sample_set_lines = self.handler.connection.post.call_args[1]["body"][
            "sampleSetLines"
        ]
        first_line_fields = {
            field["name"]: field["value"] for field in sample_set_lines[0]["fields"]
        }
        # Converting the fields in the first sample set line to a dictionary for easier
        # testing
        assert first_line_fields["MethodSetOrReportMethod"] == "test_method_1"
        assert first_line_fields["Vial"] == "test_sample_pos_1"
        assert first_line_fields["SampleName"] == "test_sample_name_1"
        assert first_line_fields["InjVol"] == 1
        second_line_fields = {
            field["name"]: field["value"] for field in sample_set_lines[1]["fields"]
        }
        # Converting the fields in the second sample set line to a dictionary for easier
        # testing
        assert second_line_fields["MethodSetOrReportMethod"] == "test_method_2"
        assert second_line_fields["Vial"] == "test_sample_pos_2"
        assert second_line_fields["SampleName"] == "test_sample_name_2"
        assert second_line_fields["InjVol"] == 2
        assert second_line_fields["test_field_1"] == "test_value"
        assert second_line_fields["test_field_2"] == 2.3
        int_type_list = [
            field["dataType"]
            for field in sample_set_lines[0]["fields"]
            if isinstance(field["value"], int)
        ]
        assert all(
            [int_type == "Double" for int_type in int_type_list]
        )  # Testing that all integer values are doubles
        float_type_list = [
            field["dataType"]
            for field in sample_set_lines[0]["fields"]
            if isinstance(field["value"], float)
        ]
        assert all([float_type == "Double" for float_type in float_type_list])
        # Testing that all float values are doubles
        string_type_list = [
            field["dataType"]
            for field in sample_set_lines[0]["fields"]
            if isinstance(field["value"], str)
        ]
        assert all([string_type == "String" for string_type in string_type_list])
        # Testing that all string values are strings
        dict_type_list = [
            field["dataType"]
            for field in sample_set_lines[0]["fields"]
            if isinstance(field["value"], dict)
        ]
        assert all([dict_type == "Enumerator" for dict_type in dict_type_list])
        # Testing that all dictionary values are strings

    def test_post_sample_list_with_empower_names(self):
        sample_list = [
            {
                "MethodSetOrReportMethod": "test_method_1",
                "Vial": "test_sample_pos_1",
                "InjVol": 1,
                "SampleName": "test_sample_name_1",
            },
        ]
        self.handler.PostExperiment(
            sample_set_method_name="test_sampleset_name",
            sample_list=sample_list,
            plates={},
            audit_trail_message="test_audit_trail_message",
        )
        sample_set_lines = self.handler.connection.post.call_args[1]["body"][
            "sampleSetLines"
        ]
        sample_fields = {
            field["name"]: field["value"] for field in sample_set_lines[0]["fields"]
        }
        assert sample_fields["MethodSetOrReportMethod"] == "test_method_1"
        assert sample_fields["Vial"] == "test_sample_pos_1"
        assert sample_fields["InjVol"] == 1

    def test_post_sample_list_plates(self):
        plates = {"1": "test_plate_name_1", "2": "test_plate_name_2"}
        self.handler.PostExperiment(
            sample_set_method_name="test_sampleset_name",
            sample_list=[],
            plates=plates,
            audit_trail_message="test_audit_trail_message",
        )
        plate_definition_list = [
            {"plateTypeName": plate_name, "plateLayoutPosition": plate_pos}
            for (plate_pos, plate_name) in plates.items()
        ]
        for plate_definiton in plate_definition_list:
            assert (
                plate_definiton
                in self.handler.connection.post.call_args[1]["body"]["plates"]
            )

    def test_components(self):
        component_dict = {"test_component_name_1": 1, "test_component_name_2": 2}
        sample_list = [
            {
                "Method": "test_method_1",
                "SamplePos": "test_sample_pos_1",
                "SampleName": "test_sample_name_1",
                "InjectionVolume": 1,
                "Components": component_dict,
            },
        ]
        self.handler.PostExperiment(
            sample_set_method_name="test_sampleset_name",
            sample_list=sample_list,
            plates={},
            audit_trail_message="test_audit_trail_message",
        )
        sample_set_lines = self.handler.connection.post.call_args[1]["body"][
            "sampleSetLines"
        ]
        components = sample_set_lines[0]["components"]
        assert components[0]["id"] != components[1]["id"]
        for i, (name, concentration) in enumerate(component_dict.items()):
            name_dict = {"name": "Component", "value": name, "dataType": "String"}
            assert name_dict in components[i]["fields"]
            concentration_dict = {
                "name": "Value",
                "value": concentration,
                "dataType": "Double",
            }
            assert concentration_dict in components[i]["fields"]

    def test_component_key(self):
        component_dict = {"test_component_name_1": 1}
        sample_list = [
            {
                "Method": "test_method_1",
                "SamplePos": "test_sample_pos_1",
                "SampleName": "test_sample_name_1",
                "InjectionVolume": 1,
                "Components": "test_custom_field_value",
                "StandardComponents": component_dict,
            },
        ]
        self.handler.PostExperiment(
            sample_set_method_name="test_sampleset_name",
            sample_list=sample_list,
            plates={},
            audit_trail_message="test_audit_trail_message",
            component_key="StandardComponents",
        )
        sample_set_lines = self.handler.connection.post.call_args[1]["body"][
            "sampleSetLines"
        ]
        components = sample_set_lines[0]["components"]
        assert {
            "name": "Component",
            "value": "test_component_name_1",
            "dataType": "String",
        } in components[0]["fields"]
        assert {"name": "Value", "value": 1, "dataType": "Double"} in components[0][
            "fields"
        ]
        assert {
            "name": "Components",
            "value": "test_custom_field_value",
            "dataType": "String",
        } in sample_set_lines[0]["fields"]


class TestGetMethods(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_get_method_list(self):
        self.handler.connection.get.return_value = create_empower_response(
            [
                {
                    "fields": [
                        {"name": "Name", "value": "test_method_name_1"},
                        {"name": "irrelevant_field", "value": "irrelevant_value"},
                    ]
                },
                {
                    "fields": [
                        {"name": "Name", "value": "test_method_name_2"},
                        {"name": "irrelevant_field", "value": "irrelevant_value"},
                    ]
                },
            ]
        )

        method_list = self.handler.GetMethodList()
        assert method_list == ["test_method_name_1", "test_method_name_2"]
        assert (
            "methodTypes=MethodSetMethod"
            in self.handler.connection.get.call_args[1]["endpoint"]
        )  # Check that the correct parameters are passed to the request

    def test_method_with_no_name(self):
        self.handler.connection.get.return_value = create_empower_response(
            [
                {
                    "fields": [
                        {"name": "Name", "value": "test_method_name_1"},
                        {"name": "irrelevant_field", "value": "irrelevant_value"},
                    ]
                },
                {
                    "fields": [
                        {"name": "no_Name", "value": "test_method_name_2"},
                        {"name": "irrelevant_field", "value": "irrelevant_value"},
                    ]  # No fields with name "Name" should give an error
                },
            ],
        )
        with self.assertRaises(ValueError):
            self.handler.GetMethodList()

    def test_method_with_two_names(self):
        self.handler.connection.get.return_value = create_empower_response(
            [
                {
                    "fields": [
                        {"name": "Name", "value": "test_method_name_1"},
                        {"name": "Name", "value": "irrelevant_value"},
                    ]  # Two fields with name "Name" should give an error
                },
                {
                    "fields": [
                        {"name": "Name", "value": "test_method_name_2"},
                        {"name": "irrelevant_field", "value": "irrelevant_value"},
                    ]
                },
            ],
        )
        with self.assertRaises(ValueError):
            self.handler.GetMethodList()

    def test_get_sample_set_method_list(self):
        self.handler.connection.get.return_value = create_empower_response(
            ["test_samplesetmethod_1"]
        )
        samplesetmethod_list = self.handler.GetSampleSetMethods()
        assert samplesetmethod_list == ["test_samplesetmethod_1"]
        assert (
            "project/methods/sample-set-method-list"
            == self.handler.connection.get.call_args[1]["endpoint"]
        )

    def test_get_other_method(self):
        self.handler.GetMethodList(method_type="OtherMethod")
        assert (
            "methodTypes=OtherMethod"
            in self.handler.connection.get.call_args[1]["endpoint"]
        )

    def test_implicit_method_name(self):
        self.handler.GetMethodList(method_type="Other")
        assert (
            "methodTypes=OtherMethod"
            in self.handler.connection.get.call_args[1]["endpoint"]
        )


class TestGetPlateTypes(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_get_plate_type_names(self):
        self.handler.connection.get.return_value = create_empower_response(
            [
                "test_plate_type_name_1",
                "test_plate_type_name_2",
            ],
        )
        plate_type_names = self.handler.GetPlateTypeNames()
        assert plate_type_names == [
            "test_plate_type_name_1",
            "test_plate_type_name_2",
        ]

    def test_get_plate_type_names_filter(self):
        self.handler.GetPlateTypeNames(filter_string="test_filter_text")
        assert (
            "?stringFilter=test_filter_text"
            in self.handler.connection.get.call_args[1]["endpoint"]
        )


class TestLogin(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_login_error_without_context_management(self):
        """
        Tests that an error is rasied if the used tries to log in without using the
        context manager if the EmpowerHandler is set to not allow it.
        """
        with self.assertRaises(RuntimeError):
            self.handler.login()

    def test_loging_warning_without_context_management(self):
        """
        Tests that a warning is raised if the user tries to log in without using the
        context manager if the EmpowerHandler is set to allow it.
        """
        self.handler.allow_login_without_context_manager = True
        with self.assertWarns(Warning):
            self.handler.login()

    def test_context_management(self):
        with self.handler:
            pass
        assert self.handler.connection.login.call_count == 1
        # Check that the login method is called when entering the context manager
        assert self.handler.connection.logout.call_count == 1
        # Check that the logout method is called when exiting the context manager

    def test_no_autologin(self):
        self.handler.auto_login = False
        with self.handler:
            pass
        assert self.handler.connection.login.call_count == 0

    def test_context_no_autologin(self):
        self.handler.auto_login = False
        with self.handler:
            self.handler.login()


class TestUsername(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_username_setter(self):
        self.handler.username = "test_username"
        assert self.handler.connection.username == "test_username"

    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def test_username_on_creation(self, mock_connection):
        mock_response = MagicMock
        mock_connection.return_value = mock_response
        EmpowerHandler(
            project="test_project",
            address="https://test_address/",
            username="test_username",
        )
        assert mock_connection.call_args[1]["username"] == "test_username"

    def test_function(self):
        self.handler.PostExperiment(
            sample_set_method_name="",
            sample_list=[
                {"SampleName": ""},
                {"SampleName": "", "Function": "Purge Inj"},
            ],
            plates={},
        )
        field_list_list = [
            sample_set_line["fields"]
            for sample_set_line in self.handler.connection.post.call_args[1]["body"][
                "sampleSetLines"
            ]
        ]
        function_dict_list = [
            [field for field in field_list if field["name"] == "Function"][0]
            for field_list in field_list_list
        ]
        assert function_dict_list[0]["value"] == {"member": "Inject Samples"}
        assert function_dict_list[1]["value"] == {"member": "Purge Inj"}


class TestInstrumentMethodInteraction(unittest.TestCase):
    # We need to patch the EmpowerConnection class, because it is used in the
    # EmpowerHandler class. But we don't really need it to do anything, so we just
    # let mock handle it. We still need to give it as an argument to the setUp method,
    # so we call it _ to indicate that we don't use it.
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_get_method_api_version_one(self):
        minimal_module = {
            "name": "test",
            "nativeXml": "test_name",
        }
        self.handler.connection.api_version = "1.0"
        self.handler.connection.get.return_value = create_empower_response(
            [{"methodName": "test_method", "modules": [minimal_module]}],
        )
        method = self.handler.GetInstrumentMethod("test_method_name")
        assert self.handler.connection.get.call_args[1]["endpoint"] == (
            "project/methods/instrument-method?name=test_method_name"
        )
        assert isinstance(method, EmpowerInstrumentMethod)
        assert len(method.module_method_list) == 1
        assert isinstance(method.module_method_list[0], EmpowerModuleMethod)
        assert method.module_method_list[0].original_method == minimal_module

    def test_get_method_api_version_two(self):
        minimal_module = {
            "name": "test",
            "nativeXml": "test_name",
        }
        self.handler.connection.api_version = "2.0"
        self.handler.connection.get.return_value = create_empower_response(
            {"methodName": "test_method", "modules": [minimal_module]},
        )
        method = self.handler.GetInstrumentMethod("test_method_name")
        assert self.handler.connection.get.call_args[1]["endpoint"] == (
            "project/methods/instrument-method?name=test_method_name"
        )
        assert isinstance(method, EmpowerInstrumentMethod)
        assert len(method.module_method_list) == 1
        assert isinstance(method.module_method_list[0], EmpowerModuleMethod)
        assert method.module_method_list[0].original_method == minimal_module

    def test_post_method(self):
        minimal_module = {
            "name": "test",
            "nativeXml": (
                "<test_tag1>test_value1</test_tag1>"
                "<test_tag2>test_value2</test_tag2>"
            ),
        }

        self.handler.connection.get.return_value = create_empower_response(
            {"methodName": "test_method", "modules": [minimal_module]},
        )
        self.handler.connection.api_version = "2.0"
        method = self.handler.GetInstrumentMethod("test_method_name")
        method.module_method_list[0].replace("test_value1", "new_value")
        method.module_method_list[0]["test_tag2"] = "newer_value"
        self.handler.PostInstrumentMethod(method)
        assert self.handler.connection.post.call_args[1]["endpoint"] == (
            "project/methods/instrument-method?overWriteExisting=false"
        )
        assert (
            self.handler.connection.post.call_args[1]["body"]["modules"][0]["nativeXml"]
            == "<test_tag1>new_value</test_tag1><test_tag2>newer_value</test_tag2>"
        )


class TestMethodSetMethodInteraction(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_get_api_version_one(self):
        self.handler.connection.get.return_value = create_empower_response(
            [{"name": "test_method_return_name"}],
        )
        self.handler.connection.api_version = "1.0"
        method = self.handler.GetMethodSetMethod("test_method_name")
        assert self.handler.connection.get.call_args[1]["endpoint"] == (
            "project/methods/method-set?name=test_method_name"
        )
        assert method["name"] == "test_method_return_name"

    def test_get_api_version_two(self):
        self.handler.connection.get.return_value = create_empower_response(
            {"name": "test_method_return_name"},
        )
        self.handler.connection.api_version = "2.0"
        method = self.handler.GetMethodSetMethod("test_method_name")
        assert self.handler.connection.get.call_args[1]["endpoint"] == (
            "project/methods/method-set?name=test_method_name"
        )
        assert method["name"] == "test_method_return_name"

    def test_post(self):
        self.handler.PostMethodSetMethod(
            {"name": "test_method_name", "test_field": "test_value"}
        )
        assert self.handler.connection.post.call_args[1]["endpoint"] == (
            "project/methods/method-set"
        )
        assert self.handler.connection.post.call_args[1]["body"]["name"] == (
            "test_method_name"
        )


class TestStatus(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )

    def test_get(self):
        self.handler.connection.get.return_value = create_empower_response(
            [
                {"name": "FirstKey", "value": "FirstValue"},
                {"name": "SecondKey", "value": "SecondValue"},
            ],
        )
        result = self.handler.GetStatus(node="test_node", system="test_system")
        assert self.handler.connection.get.call_args[1]["endpoint"] == (
            "acquisition/chromatographic-system-status"
            "?nodeName=test_node&systemName=test_system"
        )
        assert result == {"FirstKey": "FirstValue", "SecondKey": "SecondValue"}


class TestSampleSetLineFields(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
            allow_login_without_context_manager=True,
        )
        self.handler.connection.get.return_value = (
            [
                {
                    "name": "NameField",
                    "type": "Name",
                    "displayName": "Name Field Display Name",
                },
                {
                    "name": "EnumField",
                    "type": "Enumerator",
                    "displayName": "Enum Field Display Name",
                },
            ],
        )
        self.handler.login()

    def test_called_on_login(self):
        self.assertEqual(
            self.handler.connection.get.call_args[0][0],
            "/project/fields?fieldType=SampleSetLine",
        )

    def test_synonym(self):
        self.assertIn("Name Field Display Name", self.handler.synonym_dict)
        self.assertEqual(
            self.handler.synonym_dict["Name Field Display Name"], "NameField"
        )
        self.assertIn("Enum Field Display Name", self.handler.synonym_dict)
        self.assertEqual(
            self.handler.synonym_dict["Enum Field Display Name"], "EnumField"
        )

    def test_enum(self):
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=[{"EnumField": "Value1"}],
            plates={},
        )
        posted_sampleset_fields = self.handler.connection.post.call_args[1]["body"][
            "sampleSetLines"
        ][0]["fields"]
        self.assertIn(
            {
                "name": "EnumField",
                "value": {"member": "Value1"},
                "dataType": "Enumerator",
            },
            posted_sampleset_fields,
        )

    def test_explicitly_setting_allowed_values(self):
        self.handler.SetAllowedSamplesetLineFieldValues(
            "EnumField", ("Value1", "Value2")
        )
        sample_list_without_failed_field = [{"EnumField": "Value1"}]
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=sample_list_without_failed_field,
            plates={},
        )
        sample_list_with_failed_field = [{"EnumField": "Value3"}]
        with self.assertRaises(ValueError):
            self.handler.PostExperiment(
                sample_set_method_name="test",
                sample_list=sample_list_with_failed_field,
                plates={},
            )

    def test_implicitly_setting_allowed_values(self):
        self.handler.connection.get.return_value = (
            [{"member": "Value1"}, {"member": "Value2"}],
        )
        self.handler.SetAllowedSamplesetLineFieldValues("EnumField")
        sample_list_without_failed_field = [{"EnumField": "Value1"}]
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=sample_list_without_failed_field,
            plates={},
        )
        sample_list_with_failed_field = [{"EnumField": "Value3"}]
        with self.assertRaises(ValueError):
            self.handler.PostExperiment(
                sample_set_method_name="test",
                sample_list=sample_list_with_failed_field,
                plates={},
            )

    def test_setting_allowed_values_with_synonym(self):
        self.handler.SetAllowedSamplesetLineFieldValues(
            "Enum Field Display Name", ("Value1", "Value2")
        )
        sample_list_without_failed_field = [{"EnumField": "Value1"}]
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=sample_list_without_failed_field,
            plates={},
        )
        sample_list_with_failed_field = [{"EnumField": "Value3"}]
        with self.assertRaises(ValueError):
            self.handler.PostExperiment(
                sample_set_method_name="test",
                sample_list=sample_list_with_failed_field,
                plates={},
            )

    def test_overwrite_allowed_values(self):
        self.handler.SetAllowedSamplesetLineFieldValues(
            "EnumField", ("Value1", "Value2")
        )
        self.handler.SetAllowedSamplesetLineFieldValues(
            "EnumField", ("Value3", "Value4"), overwrite=False
        )
        sample_list_with_old_field = [{"EnumField": "Value1"}]
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=sample_list_with_old_field,
            plates={},
        )
        sample_list_with_new_fielda = [{"EnumField": "Value3"}]
        with self.assertRaises(ValueError):
            self.handler.PostExperiment(
                sample_set_method_name="test",
                sample_list=sample_list_with_new_fielda,
                plates={},
            )
        self.handler.SetAllowedSamplesetLineFieldValues(
            "EnumField", ("Value3", "Value4"), overwrite=True
        )
        self.handler.PostExperiment(
            sample_set_method_name="test",
            sample_list=sample_list_with_new_fielda,
            plates={},
        )
        with self.assertRaises(ValueError):
            self.handler.PostExperiment(
                sample_set_method_name="test",
                sample_list=sample_list_with_old_field,
                plates={},
            )


class TestLogout(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def setUp(self, _) -> None:
        self.handler = EmpowerHandler(
            project="test_project",
            address="https://test_address/",
        )
        self.username = "test_username"

        def mock_get(endpoint, *args, **kwargs):
            if "session-infoes" in endpoint:
                return (
                    [
                        {"user": self.username, "id": "test_session_1"},
                        {"user": self.username, "id": "test_session_2"},
                        {"user": "another_user", "id": "test_session_3"},
                        {"user": "another_user", "id": "test_session_4"},
                    ],
                )
            else:
                return ([],)

        self.mock_get = mock_get

    def test_autologout_in_context_handler(self):
        with self.handler:
            pass
        assert self.handler.connection.logout.call_count == 1

    def test_logout(self):
        self.handler.logout()
        assert self.handler.connection.logout.call_count == 1

    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def test_logout_all_sessions(self, mock_connection):
        mock_connection.return_value.get = self.mock_get
        mock_connection.return_value.username = self.username
        EmpowerHandler.LogoutAllSessions(
            address="https://test_address/", password="test_password"
        )
        assert mock_connection.return_value.logout.call_count == 3
        # Three times, two for the list, one for the handler made to log out

    @patch("OptiHPLCHandler.empower_handler.EmpowerConnection")
    def test_logout_order(self, mock_connection):
        "Tests that the session we use to log out is the last one to be logged out"
        mock_connection.return_value.get = self.mock_get
        mock_connection.return_value.username = self.username
        mock_connection.return_value.session_id = "test_session_1"
        EmpowerHandler.LogoutAllSessions(
            address="https://test_address/", password="test_password"
        )
        assert mock_connection.return_value.logout.call_count == 2
        # Only two times, since the session we used to log out is removed from the list
        # of sessions to explicitly log out from.


if __name__ == "__main__":
    unittest.main(verbosity=2)
