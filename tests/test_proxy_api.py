import unittest
from unittest.mock import MagicMock, patch

from OptiHPLCHandler import EmpowerHandler


class TestEmpowerHandler(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def setUp(self, mock_requests, mock_getpass) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"netServiceName": "test_service"}]
        }
        # Service name is automatically requested, so we need to mock that response
        mock_requests.get.return_value = mock_response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        # The connection logs in automatically, so we need to mock that response

        mock_password = MagicMock()
        mock_password.return_value = "test_password"
        self.mock_password = mock_password
        mock_getpass.return_value = mock_password
        # getpass is used to get the password, so we need to mock that response since
        # interactivity is not possible for automated testing.

        self.handler = EmpowerHandler(
            project="test_project",
            address="http://test_address/",
            username="test_username",
        )

    def test_empower_handler_initialisation(self):
        assert self.handler.project == "test_project"
        assert self.handler.username == "test_username"
        assert self.handler.address == "http://test_address/"
        assert self.handler.connection.address == "http://test_address/"
        assert self.handler.connection.username == "test_username"
        assert self.handler.connection.project == "test_project"
        assert self.handler.connection.service == "test_service"

    def test_empower_handler_status(self):
        with self.assertRaises(NotImplementedError):
            self.handler.Status()

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_post_sample_list(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": "mock_results"}
        mock_response.status_code = 201
        mock_requests.post.return_value = mock_response

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
        assert "test_sampleset_name" == mock_requests.method_calls[0][2]["json"]["name"]
        # Testing that the name is correct in the request
        assert (
            "?auditTrailComment=test_audit_trail_message"
            in mock_requests.method_calls[0][1][0]
        )
        # Testing that the audit trail message is correct
        sample_set_lines = mock_requests.method_calls[0][2]["json"]["sampleSetLines"]
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

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_post_sample_list_with_empower_names(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_requests.post.return_value = mock_response
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
        sample_set_lines = mock_requests.method_calls[0][2]["json"]["sampleSetLines"]
        sample_fields = {
            field["name"]: field["value"] for field in sample_set_lines[0]["fields"]
        }
        assert sample_fields["MethodSetOrReportMethod"] == "test_method_1"
        assert sample_fields["Vial"] == "test_sample_pos_1"
        assert sample_fields["InjVol"] == 1

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_post_sample_list_plates(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": "mock_results"}
        mock_response.status_code = 201
        mock_requests.post.return_value = mock_response
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
            assert plate_definiton in mock_requests.post.call_args[1]["json"]["plates"]

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_post_sample_list_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": "mock_results"}
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response
        with self.assertRaises(ValueError) as context:
            self.handler.PostExperiment(
                sample_set_method_name="test_sampleset_name",
                sample_list=[],
                plates={},
                audit_trail_message="test_audit_trail_message",
            )
        assert "Resource not found" in context.exception.args[0]
        mock_response.status_code = 400
        mock_response.text = "mock_error_message"
        with self.assertRaises(ValueError) as context:
            self.handler.PostExperiment(
                sample_set_method_name="test_sampleset_name",
                sample_list=[],
                plates={},
                audit_trail_message="test_audit_trail_message",
            )
        assert "Response: mock_error_message" in context.exception.args[0]

    def test_empower_handler_add_method(self):
        with self.assertRaises(NotImplementedError):
            self.handler.AddMethod(
                template_method="test_template_method",
                new_method="test_new_method",
                changes={},
                audit_trail_message="test_audit_trail_message",
            )

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_get_method_list(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
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
        }
        mock_requests.get.return_value = mock_response

        method_list = self.handler.GetMethodList()
        assert method_list == ["test_method_name_1", "test_method_name_2"]
        assert (
            "methodTypes=MethodSetMethod" in mock_requests.get.call_args[0][0]
        )  # Check that the correct parameters are passed to the request

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_method_with_no_name(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
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
            ]
        }

        mock_requests.get.return_value = mock_response
        with self.assertRaises(ValueError):
            self.handler.GetMethodList()

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_handler_method_with_two_names(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
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
            ]
        }
        mock_requests.get.return_value = mock_response
        with self.assertRaises(ValueError):
            self.handler.GetMethodList()

    def test_empower_handler_get_setup(self):
        with self.assertRaises(NotImplementedError):
            self.handler.GetSetup()

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_run_experiment_fails(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response
        with self.assertRaises(ValueError):
            self.handler.RunExperiment(
                sample_set_method="test_sample_set_method",
                node="test_node",
                hplc="test_hplc",
            )

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_empower_run_experiment(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        self.handler.RunExperiment(
            sample_set_method="test_sample_set_method",
            node="test_node",
            hplc="test_hplc",
        )
        assert (
            mock_requests.post.call_args[0][0]
            == "http://test_address/acquisition/run-sample-set-method"
        )  # Check that the correct URl is used.
        assert (
            mock_requests.post.call_args[1]["json"]["sampleSetMethodName"]
        ) == "test_sample_set_method"
        # Check that the correct sample set method is used.
        assert (
            mock_requests.post.call_args[1]["json"]["nodeName"]
        ) == "test_node"  # Check that the correct node is used.
        assert (
            mock_requests.post.call_args[1]["json"]["systemName"]
        ) == "test_hplc"  # Check that the correct HPLC is used.
        assert (
            mock_requests.post.call_args[1]["json"]["sampleSetName"]
        ) is None  # Check that no sample set name is given
        self.handler.RunExperiment(
            sample_set_method="test_sample_set_method",
            node="test_node",
            hplc="test_hplc",
            sample_set_name="test_sample_set_name",
        )
        assert (
            mock_requests.post.call_args[1]["json"]["sampleSetName"]
        ) == "test_sample_set_name"  # Check that the correct sample set name is given

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get_plate_type_names(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                "test_plate_type_name_1",
                "test_plate_type_name_2",
            ]
        }
        mock_requests.get.return_value = mock_response
        plate_type_names = self.handler.GetPlateTypeNames()
        assert plate_type_names == [
            "test_plate_type_name_1",
            "test_plate_type_name_2",
        ]

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get_plate_type_names_filter(self, mock_requests):
        mock_response = MagicMock()
        mock_requests.get.return_value = mock_response
        self.handler.GetPlateTypeNames(filter_string="test_filter_text")
        assert "?stringFilter=test_filter_text" in mock_requests.get.call_args[0][0]

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get_node_name_list(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": ["test_node_name_1"]}
        mock_requests.get.return_value = mock_response
        node_name_list = self.handler.GetNodeNames()
        assert node_name_list == ["test_node_name_1"]
        assert "acquisition/nodes" in mock_requests.get.call_args[0][0]

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get_system_name_list(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": ["test_system_name_1"]}
        mock_requests.get.return_value = mock_response
        system_name_list = self.handler.GetSystemNames("test_node_name")
        assert system_name_list == ["test_system_name_1"]
        assert (
            "acquisition/chromatographic-systems?nodeName=test_node_name"
            in mock_requests.get.call_args[0][0]
        )

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_login_pwd(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        self.handler = EmpowerHandler(
            project="test_project",
            address="http://test_address/",
            username="test_username",
            password="test_password",
        )
        assert (
            mock_requests.post.call_args[1]["json"]["password"]=="test_password"
        )