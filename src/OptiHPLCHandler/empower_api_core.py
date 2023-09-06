import getpass
import logging
import warnings
from requests import HTTPError
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
        :param username: The username to use for logging in. If None, the username of
            the user running the script is used.
        :param project: The project to use for logging in. If None, the default project
            is used.
        :param service: The service to use for logging in. If None, the first service in
            the list is used.
        :param password: The password to use for logging in. If None, the password is
            retrieved from the keyring if available, otherwise it is asked for every
            time.
        """
        self.address = address.rstrip("/")  # Remove trailing slash if present
        logger.debug("No username specified, getting username from system")
        self.username = getpass.getuser()
        if service is None:
            logger.debug("No service specified, getting service from Empower")
            response = requests.get(self.address + "/authentication/db-service-list")
            self.service = response.json()["results"][0]["netServiceName"]
            # If no service is specified, use the first one in the list
        else:
            self.service = service
        self.project = project

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
        reply = requests.post(
            self.address + "/authentication/login",
            json=body,
        )
        if reply.status_code != 200:
            logger.error("Login failed")
            raise IOError("Login failed")
        self.token = reply.json()["results"][0]["token"]
        self.session_id = reply.json()["results"][0]["id"]
        logger.debug("Login successful, keeping token")

    def logout(self) -> None:
        """Log out of Empower."""
        logger.debug("Logging out of Empower")
        reply = requests.post(
            self.address + "/authentication/logout?sessionInfoID=" + self.session_id,
            headers=self.authorization_header,
        )
        if reply.status_code == 404:
            logger.debug(
                "Logout no necessary, session already expired or were logged out."
            )
        else:
            reply.raise_for_status()
        logger.debug("Logout successful")

    def get(self, endpoint: str) -> requests.Response:
        """
        Get data from Empower.

        :param endpoint: The endpoint to get data from.
        """
        endpoint = endpoint.lstrip("/")  # Remove leading slash if present
        address = self.address + "/" + endpoint
        # Add slash between address and endpoint
        logger.debug("Getting %s", address)
        response = requests.get(address, headers=self.authorization_header)
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = requests.get(address, headers=self.authorization_header)
        logger.debug("Got response %s from %s", response.text, address)
        response.raise_for_status()
        return response

    def post(self, endpoint: str, body: dict) -> requests.Response:
        """
        Post data to Empower.

        :param endpoint: The endpoint to post data to.
        :param body: The data to post.
        """
        endpoint = endpoint.lstrip("/")  # Remove leading slash if present
        address = self.address + "/" + endpoint
        # Add slash between address and endpoint
        logger.debug("Posting %s to %s", body, address)
        response = requests.post(address, json=body, headers=self.authorization_header)
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = requests.post(
                address,
                json=body,
                headers=self.authorization_header,
            )
        logger.debug("Got respones %s from %s", response.text, address)
        response.raise_for_status()
        return response

    @property
    def password(self):
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
        return {"Authorization": "Bearer " + self.token}
