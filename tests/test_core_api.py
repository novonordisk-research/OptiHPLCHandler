import unittest
import warnings
from unittest.mock import MagicMock, patch

import requests

from OptiHPLCHandler import EmpowerConnection


class TestEmpowerConnection(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def setUp(self, mock_requests) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"token": "test_token", "id": "test_id"}]
        }
        mock_response.status_code = 200
        self.mock_response = mock_response
        mock_requests.post.return_value = mock_response
        # Since we log in, we need to mock that connection.

        mock_password = MagicMock()
        mock_password.return_value = "test_password"
        self.mock_password = mock_password
        # getpass is used to get the password, so we need to mock that response since
        # interactivity is not possible
        self.connection = EmpowerConnection(
            project="test_project",
            address="https://test_address/",
            service="test_service",
        )
        self.connection.login(username="test_username", password="test_password")
        self.verify_connection = EmpowerConnection(
            project="test_project",
            address="https://test_address/",
            service="test_service",
            verify="test/CA/path",
        )
        self.verify_connection.login("", "")

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_auto_service(self, mock_requests):
        mock_response_service = MagicMock()
        mock_response_service.json.return_value = {
            "results": [{"netServiceName": "auto_test_service"}]
        }
        # Service name is automatically requested, so we need to mock that response
        mock_response_service.status_code = 200
        mock_requests.get.return_value = mock_response_service
        connection = EmpowerConnection(
            project="test_project",
            address="http://test_address/",
        )
        assert connection.service == "auto_test_service"

    def test_set_values(self):
        assert self.connection.project == "test_project"
        assert self.connection.address == "https://test_address"
        # The trailing slash is removed
        assert self.connection.service == "test_service"
        assert self.connection.token == "test_token"
        assert self.connection.session_id == "test_id"

    def test_login_timeout(self):
        # test that the call to login times out if the server is not available
        with patch("OptiHPLCHandler.empower_api_core.requests.post") as mock_post:
            self.connection.login(username="test_username", password="test_password")
            assert "timeout" in mock_post.call_args[1]

    def test_verify_post(self):
        with patch("OptiHPLCHandler.empower_api_core.requests.request") as mock_request:
            self.connection.post("", {})
            assert mock_request.call_args[1]["verify"] is True
        with patch("OptiHPLCHandler.empower_api_core.requests.request") as mock_request:
            self.verify_connection.post("", {})
            assert mock_request.call_args[1]["verify"] == "test/CA/path"

    def test_verify_get(self):
        with patch("OptiHPLCHandler.empower_api_core.requests.request") as mock_request:
            self.connection.get("")
            assert mock_request.call_args[1]["verify"] is True
        with patch("OptiHPLCHandler.empower_api_core.requests.request") as mock_request:
            self.verify_connection.post("", {})
            assert mock_request.call_args[1]["verify"] == "test/CA/path"

    def test_verify_login(self):
        with patch("OptiHPLCHandler.empower_api_core.requests.post") as mock_request:
            self.connection.login("", "")
            assert mock_request.call_args[1]["verify"] is True
        with patch("OptiHPLCHandler.empower_api_core.requests.post") as mock_request:
            self.verify_connection.login("", "")
            assert mock_request.call_args[1]["verify"] == "test/CA/path"

    def test_verify_logout(self):
        with patch("OptiHPLCHandler.empower_api_core.requests.delete") as mock_request:
            self.connection.logout()
            assert mock_request.call_args[1]["verify"] is True
        with patch("OptiHPLCHandler.empower_api_core.requests.delete") as mock_request:
            self.verify_connection.logout()
            assert mock_request.call_args[1]["verify"] == "test/CA/path"

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_automatic_service_name(self, mock_requests):
        mock_response_service = MagicMock()
        mock_response_service.json.return_value = {
            "results": [{"netServiceName": "auto_test_service"}]
        }
        # Service name is automatically requested, so we need to mock that response
        mock_response_service.status_code = 200
        mock_requests.get.return_value = mock_response_service
        connection = EmpowerConnection(
            address="http://test_address/",
            project="test_project",
        )
        assert connection.service == "auto_test_service"

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"test_key": "test_value"}],
            "message": "test_message",
        }
        mock_requests.request.return_value = mock_response
        result_list = self.connection.get("test_url")[0]
        message = self.connection.get("test_url")[1]
        # Testing that the get method is called with the correct url
        assert mock_requests.request.call_args[0][0] == "get"
        assert mock_requests.request.call_args[0][1] == "https://test_address/test_url"
        assert "test_key" in result_list[0]
        assert result_list[0]["test_key"] == "test_value"
        assert message == "test_message"
        self.connection.get("/test_url")
        # Testing that the get method is called with the correct url when endpoint
        # starts with a slash
        assert mock_requests.request.call_args[0][1] == "https://test_address/test_url"

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_get_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        self.connection.get("test_url")
        assert mock_requests.request.return_value.raise_for_status.called

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_relogin_get(self, mock_requests, mock_getpass):
        # Verify that the handler logs in again if the token is invalid on get.
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 401
        mock_requests.request.return_value = mock_response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        self.connection.get("test_url")
        assert mock_requests.method_calls[1].args == (
            "https://test_address/authentication/login",
        )
        # The second call should be to log in

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_post(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.request.return_value = mock_response
        # The last call should be to log in, since this should casue an exception.
        self.connection.post("test_url", body={})
        # Testing that the post method is called with the correct url
        assert mock_requests.request.call_args[0][0] == "post"
        assert mock_requests.request.call_args[0][1] == "https://test_address/test_url"
        self.connection.post("/test_url", body={})
        # Testing that the get method is called with the correct url when endpoint
        # starts with a slash
        assert mock_requests.request.call_args[0][1] == "https://test_address/test_url"

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_post_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response
        self.connection.post("test_url", body="test_body")
        assert mock_requests.request.return_value.raise_for_status.called

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_relogin_post(self, mock_requests, mock_getpass):
        # Verify that the handler logs in again if the token is invalid on put.
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"token": "test_token", "id": "test_id"}]
        }
        mock_response.status_code = 401
        mock_requests.request.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        self.connection.post("test_url", body="test_body")
        assert mock_requests.method_calls[1].args == (
            "https://test_address/authentication/login",
        )
        # The second call should be to log in

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_http_warning(self, mock_requests, mock_getpass):
        # Verify that the handler warns if the connection is not https.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        self.connection.address = "http://test_address/"
        with self.assertWarns(Warning):
            self.connection.login()

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_no_warning_https(self, mock_request, mock_getpass):
        # Verify that the handler does not warn if the connection is https.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.post.return_value = mock_response
        mock_request.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        connection = EmpowerConnection(
            address="https://test_address/",
            project="test_project",
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            connection.login()

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_info_in_login_message(self, mock_request, mock_getpass):
        # Verify that the handler prints the correct info in the login message.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.post.return_value = mock_response
        mock_request.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        self.connection.login(username="test_username")
        assert "test_username" in mock_getpass.call_args[0][0]

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_logout(self, mock_requests):
        self.connection.logout()
        assert mock_requests.delete.call_args[0][0] == (
            "https://test_address/authentication/logout?sessionInfoID=test_id"
        )

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_logout_404(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests.delete.return_value = mock_response
        self.connection.logout()
        assert mock_requests.delete.call_args[0][0] == (
            "https://test_address/authentication/logout?sessionInfoID=test_id"
        )
        assert mock_response.raise_for_status.called is False
        # Asserting that an error is not raised if the logout fails with 404. This will
        # happen if the session has already expired or if the user has already logged
        # out.

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_logout_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_requests.delete.return_value = mock_response
        self.connection.logout()
        assert mock_requests.delete.return_value.raise_for_status.called

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_delete(self, mock_requests):
        del self.connection
        assert mock_requests.delete.call_args[0][0] == (
            "https://test_address/authentication/logout?sessionInfoID=test_id"
        )

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "test_message",
            "id": "test_id",
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_requests.request.return_value = mock_response
        mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.connection.get("test_url")
        assert "HTTP error 400" in str(context.exception)
        assert "message 'test_message'" in str(context.exception)
        assert "ID test_id" in str(context.exception)

    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_incomplete_json(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_requests.request.return_value = mock_response
        response = self.connection.get("test_url")
        assert response == (None, None)
        mock_response.json.return_value = {"results": []}
        response = self.connection.get("test_url")
        assert response == ([], None)
        mock_response.json.return_value = {"message": "test_message"}
        response = self.connection.get("test_url")
        assert response == (None, "test_message")
