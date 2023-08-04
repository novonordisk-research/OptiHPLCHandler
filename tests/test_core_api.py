import unittest
from unittest.mock import MagicMock, patch
import warnings

from OptiHPLCHandler import EmpowerConnection


class TestEmpowerConnection(unittest.TestCase):
    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def setUp(self, mock_requests, mock_getpass) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        # The connection logs in automatically, so we need to mock that response

        mock_password = MagicMock()
        mock_password.return_value = "test_password"
        self.mock_password = mock_password
        mock_getpass.return_value = mock_password
        # getpass is used to get the password, so we need to mock that response since interactivity is not possible
        self.connection = EmpowerConnection(
            project="test_project",
            address="http://test_address/",
            username="test_username",
            service="test_service",
        )

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_auto_service(self, mock_requests, mock_getpass):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"netServiceName": "auto_test_service", "token": "test_token"}]
        }
        mock_response.status_code = 200
        # Service name is automatically requested, so we need to mock that response
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        connection = EmpowerConnection(
            project="test_project",
            address="http://test_address/",
            username="test_username",
        )
        assert connection.service == "auto_test_service"

    def test_set_values(self):
        assert self.connection.project == "test_project"
        assert self.connection.username == "test_username"
        assert self.connection.address == "http://test_address/"
        assert self.connection.service == "test_service"
        assert self.connection.token == "test_token"

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_automatic_service_name(self, mock_requests, mock_getpass):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"netServiceName": "automatic_test_service", "token": "test_token"}
            ]
        }
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        connection = EmpowerConnection(
            address="http://test_address/",
            username="test_username",
            project="test_project",
        )
        assert connection.service == "automatic_test_service"

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_relogin_get(self, mock_requests, mock_getpass):
        # Verify that the handler logs in again if the token is invalid on get.
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        try:  # When get fails, the connection will try and log in, which should also give an error.
            # We do not care about that error, we want to verify that it tries to log in again.
            self.connection.get("test_url")
        except IOError:
            pass
        assert mock_requests.method_calls[-1].args == (
            "http://test_address/authentication/login",
        )
        # The last call should be to log in, since this should casue an exception.

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_relogin_put(self, mock_requests, mock_getpass):
        # Verify that the handler logs in again if the token is invalid on put.
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response
        mock_requests.put.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        try:  # When put fails, the connection will try and log in, which should also give an error.
            # We do not care about that error, we want to verify that it tries to log in again.
            self.connection.put("test_url", body="test_body")
        except IOError:
            pass
        assert mock_requests.method_calls[-1].args == (
            "http://test_address/authentication/login",
        )
        # The last call should be to log in, since this should casue an exception.

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_relogin_post(self, mock_requests, mock_getpass):
        # Verify that the handler logs in again if the token is invalid on put.
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"token": "test_token"}]}
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response
        mock_getpass.return_value = self.mock_password
        try:  # When put fails, the connection will try and log in, which should also give an error.
            # We do not care about that error, we want to verify that it tries to log in again.
            self.connection.post("test_url", body="test_body")
        except IOError:
            pass
        assert mock_requests.method_calls[-1].args == (
            "http://test_address/authentication/login",
        )
        # The last call should be to log in, since this should casue an exception.

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_login_fail(self, mock_requests, mock_getpass):
        # Verify that the handler raises an IO error if the login fails.
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password

        with self.assertRaises(IOError):
            self.connection.login()

    @patch("OptiHPLCHandler.empower_api_core.getpass.getpass")
    @patch("OptiHPLCHandler.empower_api_core.requests")
    def test_http_warning(self, mock_requests, mock_getpass):
        # Verify that the handler warns if the connection is not https.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response
        mock_getpass.return_value = self.mock_password
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
            username="test_username",
            project="test_project",
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            connection.login()
