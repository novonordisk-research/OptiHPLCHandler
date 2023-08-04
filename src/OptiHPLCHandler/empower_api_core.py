import getpass
import warnings
from typing import Optional

import keyring
import requests
from keyring.errors import NoKeyringError


class EmpowerConnection:
    def __init__(
        self,
        address: str,
        username: Optional[str] = None,
        project: Optional[str] = None,
        service: Optional[str] = None,
    ) -> None:
        self.address = address
        if username is None:
            self.username = getpass.getuser()
        else:
            self.username = username
        if service is None:
            response = requests.get(self.address + "authentication/db-service-list")
            self.service = response.json()["results"][0]["netServiceName"]
            # If no service is specified, use the first one in the list
        else:
            self.service = service
        self.project = project
        self.login()

    def login(self) -> None:
        body = {
            "service": self.service,
            "userName": self.username,
            "password": self.password,
        }
        if self.project is not None:
            # If no project is given, log into the default project, e.g. "Mobile"
            body["project"] = self.project
        reply = requests.post(
            self.address + "authentication/login",
            json=body,
        )
        if reply.status_code != 200:
            raise IOError("Login failed")
        self.token = reply.json()["results"][0]["token"]

    def get(self, endpoint: str) -> requests.Response:
        response = requests.get(
            self.address + endpoint, headers={"Authorization": "Bearer " + self.token}
        )
        if response.status_code == 401:
            self.login()
            response = requests.get(
                self.address + endpoint,
                headers={"Authorization": "Bearer " + self.token},
            )
        return response

    def put(self, endpoint: str, body: dict) -> requests.Response:
        response = requests.put(
            self.address + endpoint,
            json=body,
            headers={"Authorization": "Bearer " + self.token},
        )
        if response.status_code == 401:
            self.login()
            response = requests.put(
                self.address + endpoint,
                json=body,
                headers={"Authorization": "Bearer " + self.token},
            )
        return response

    def post(self, endpoint: str, body: dict) -> requests.Response:
        response = requests.post(
            self.address + endpoint,
            json=body,
            headers={"Authorization": "Bearer " + self.token},
        )
        if response.status_code == 401:
            self.login()
            response = requests.post(
                self.address + endpoint,
                json=body,
                headers={"Authorization": "Bearer " + self.token},
            )
        return response

    @property
    def password(self):
        try:
            password = keyring.get_password("Empower", self.username)
        except (
            NoKeyringError
        ):  # If no keyring is available, ask for password. This is the case in Datalab.
            password = None
        if not password:
            if not self.address.startswith("https"):
                warnings.warn("The password will be sent in plain text.")
            password = getpass.getpass(
                f"Please enter the password for user {self.username}: "
            )
        return password
