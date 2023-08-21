import getpass
import logging
import warnings
from typing import Optional

import keyring
import requests
from keyring.errors import NoKeyringError

logger = logging.getLogger(__name__)


class EmpowerConnection:
    def __init__(
        self,
        address: str,
        username: Optional[str] = None,
        project: Optional[str] = None,
        service: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.address = address
        if username is None:
            logger.debug("No username specified, getting username from system")
            self.username = getpass.getuser()
        else:
            self.username = username
        if service is None:
            logger.debug("No service specified, getting service from Empower")
            response = requests.get(self.address + "authentication/db-service-list")
            self.service = response.json()["results"][0]["netServiceName"]
            # If no service is specified, use the first one in the list
        else:
            self.service = service
        self.project = project
        self.login(password)

    def login(self, password: Optional[str] = None) -> None:
        if not password:
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
            self.address + "authentication/login",
            json=body,
        )
        if reply.status_code != 200:
            logger.error("Login failed")
            raise IOError("Login failed")
        self.token = reply.json()["results"][0]["token"]
        logger.debug("Login successful, keeping token")

    def get(self, endpoint: str) -> requests.Response:
        logger.debug(f"Getting {endpoint}")
        response = requests.get(
            self.address + endpoint, headers={"Authorization": "Bearer " + self.token}
        )
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = requests.get(
                self.address + endpoint,
                headers={"Authorization": "Bearer " + self.token},
            )
        logger.debug("Got response %s from %s", response.text, endpoint)
        return response

    def put(self, endpoint: str, body: dict) -> requests.Response:
        logger.debug("Putting %s to %s", body, endpoint)
        response = requests.put(
            self.address + endpoint,
            json=body,
            headers={"Authorization": "Bearer " + self.token},
        )
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = requests.put(
                self.address + endpoint,
                json=body,
                headers={"Authorization": "Bearer " + self.token},
            )
        logger.debug("Got respones %s from %s", response.text, endpoint)
        return response

    def post(self, endpoint: str, body: dict) -> requests.Response:
        logger.debug("Posting %s to %s", body, endpoint)
        response = requests.post(
            self.address + endpoint,
            json=body,
            headers={"Authorization": "Bearer " + self.token},
        )
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = requests.post(
                self.address + endpoint,
                json=body,
                headers={"Authorization": "Bearer " + self.token},
            )
        logger.debug("Got respones %s from %s", response.text, endpoint)
        return response

    @property
    def password(self):
        try:
            password = keyring.get_password("Empower", self.username)
            logger.debug("Password found in keyring")
        except (
            NoKeyringError
        ):  # If no keyring is available, ask for password. This is the case in Datalab.
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
