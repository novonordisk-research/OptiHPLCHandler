import getpass
import inspect
import logging
import warnings
from typing import Optional

import keyring
import requests
from keyring.errors import NoKeyringError

logger = logging.getLogger(__name__)


class EmpowerConnection:
    """
    Class for handling connection to Empower.

    Since the purpose of this handler is not to change date in Empower, it does not have
    a put() method, only get() and post().

    The connection is kept open by storing a bearer token provided by Empower.

    If the token expires, the connection is automatically  reestablished.

    The password is stored in the keyring if available, otherwise it is asked for every
    time.

    :attribute address: The address of the Empower server.
    :attribute username: The username to use for logging in.
    :attribute project: The project to log into.
    :attribute service: The service to use for logging in.
    :attribute token: The bearer token used for authentication.
    """

    def __init__(
        self,
        address: str,
        project: Optional[str] = None,
        service: Optional[str] = None,
    ) -> None:
        """
        Initialize the EmpowerConnection.

        :param address: The address of the Empower server.
        :param project: The project to use for logging in. If None, the default project
            is used.
        :param service: The service to use for logging in. If None, the first service in
            the list is used.
        """
        self.address = address.rstrip("/")  # Remove trailing slash if present
        self.username = getpass.getuser()
        if service is None:
            logger.debug("No service specified, getting service from Empower")
            try:
                response = requests.get(
                    self.address + "/authentication/db-service-list", timeout=10
                )
            except requests.exceptions.Timeout as e:
                print(f"Getting service from {self.address} timed out")
                logger.error("Getting service from %s timed out", self.address)
                raise Exception(f"Getting service from {self.address} timed out") from e
            self.service = response.json()["results"][0]["netServiceName"]
            # If no service is specified, use the first one in the list
        else:
            self.service = service
        self.project = project
        self.session_id = None
        self.token = None

    def login(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """
        Log into Empower.

        :param password: The password to use for logging in. If None, the password is
            retrieved from the keyring if available, otherwise it is asked for every
            time.
        :param username: The username to use for logging in. If None, the username of
            the default user is used. When EmpowerConnection is initialized, the
            username of the user running the script is set to the default username. If
            login is called with a different username, the default username is changed
            to the given username.
        """
        if username is not None:
            self.username = username
        if password is None:
            password = self.password
        body = {
            "service": self.service,
            "userName": self.username,
            "password": password,
        }
        if self.project is not None:
            # If no project is given, log into the default project, e.g. "Mobile"
            body["project"] = self.project
        logger.debug("Logging into Empower")
        try:
            reply = requests.post(
                self.address + "/authentication/login",
                json=body,
                timeout=60,
            )
        except requests.exceptions.Timeout as e:
            print(f"Login to {self.address} with username = {self.username} timed out")
            logger.error(
                "Login to %s with username = %s timed out", self.address, self.username
            )
            raise Exception(
                f"Login to {self.address} with username = {self.username} timed out"
            ) from e
        reply.raise_for_status()
        self.token = reply.json()["result"]["token"]
        self.session_id = reply.json()["result"]["id"]
        logger.debug("Login successful, keeping token")

    def logout(self) -> None:
        """Log out of Empower."""
        if self.session_id is None:
            logger.debug("No session ID, no need to log out")
            return
        logger.debug("Logging out of Empower")
        reply = requests.delete(
            self.address + "/authentication/logout?sessionInfoID=" + self.session_id,
            headers=self.authorization_header,
        )
        if reply.status_code == 404:
            logger.debug(
                "Logout no necessary, session already expired or were logged out."
            )
        else:
            reply.raise_for_status()
        self.session_id = None
        logger.debug("Logout successful")

    def _requests_wrapper(
        self, method: str, endpoint: str, body: Optional[dict], timeout
    ) -> requests.Response:
        """
        Wrapper for requests.

        :param method: The method to use.
        :param endpoint: The endpoint to use.
        :param body: The body to use.
        """

        def _request_with_timeout(method, endpoint, header, body, timeout):
            try:
                response = requests.request(
                    method,
                    endpoint,
                    json=body,
                    headers=header,
                    timeout=timeout,
                )
            except requests.exceptions.Timeout as e:
                print(f"{method}ing {body} to {endpoint} timed out")
                logger.error("%sing %s to %s timed out", method, body, endpoint)
                raise Exception(f"{method}ing {body} to {endpoint} timed out") from e
            return response

        endpoint = endpoint.lstrip("/")  # Remove leading slash if present
        address = self.address + "/" + endpoint
        # Add slash between address and endpoint
        logger.debug("%sing %s to %s", method, body, address)
        response = _request_with_timeout(
            method, address, self.authorization_header, body, timeout
        )
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = _request_with_timeout(
                method, address, self.authorization_header, body, timeout
            )
        logger.debug("Got response %s from %s", response.text, address)
        response.raise_for_status()
        return response

    def get(self, endpoint: str, timeout=10) -> requests.Response:
        """
        Get data from Empower.

        :param endpoint: The endpoint to get data from.
        """
        signature = inspect.signature(self.get)
        logger.debug("Getting data from %s", endpoint)
        if signature.parameters["timeout"].default != timeout:
            logger.debug("Timeout changed from default value to %s", timeout)
            print(
                f"Get call to endpoint {endpoint} could be slow, "
                f"timeout is set to {timeout} seconds"
            )
        return self._requests_wrapper(
            method="get", endpoint=endpoint, body=None, timeout=timeout
        )

    def post(self, endpoint: str, body: dict, timeout=10) -> requests.Response:
        """
        Post data to Empower.

        :param endpoint: The endpoint to post data to.
        :param body: The data to post.
        """
        signature = inspect.signature(self.post)
        logger.debug("Posting data %s to %s", body, endpoint)
        if signature.parameters["timeout"].default != timeout:
            logger.debug("Timeout changed from default value to %s", timeout)
            print(
                f"Post call to endpoint {endpoint} could be slow, "
                f"timeout is set to {timeout} seconds"
            )
        response = self._requests_wrapper(
            method="post", endpoint=endpoint, body=body, timeout=timeout
        )
        return response

    @property
    def password(self):
        """Get the password to use for logging in."""
        try:
            password = keyring.get_password("Empower", self.username)
            logger.debug("Password found in keyring")
        except NoKeyringError:
            # If no keyring is available, ask for password. This is the case in Datalab.
            password = None
            logger.debug("No keyring found")
        if not password:
            logger.debug("No password found in keyring, asking user for password")
            if not self.address.startswith("https"):
                warnings.warn("The password will be sent in plain text.")
            password = getpass.getpass(
                f"Please enter the password for user {self.username}: "
            )
        return password

    @property
    def authorization_header(self):
        """Get the authorization header to use for requests."""
        return {"Authorization": "Bearer " + self.token}

    def __del__(self):
        if self.session_id is not None:
            self.logout()
