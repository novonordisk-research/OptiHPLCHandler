import getpass
import logging
import warnings
from typing import Optional, Tuple, Union

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

    :ivar address: The address of the Empower server.
    :ivar username: The username to use for logging in.
    :ivar project: The project to log into.
    :ivar service: The service to use for logging in.
    :ivar token: The bearer token used for authentication.
    :ivar session_id: The session ID. None if not logged in.
    :ivar default_get_timeout: The default timeout to use for get requests.
    :ivar default_post_timeout: The default timeout to use for post requests.
    :ivar verify: Whether to verify SSL certificates when connecting via HTTPS.
    """

    def __init__(
        self,
        address: str,
        project: Optional[str] = None,
        service: Optional[str] = None,
        verify: Union[bool, str] = True,
    ) -> None:
        """
        Initialize the EmpowerConnection.

        :param address: The address of the Empower server.
        :param project: The project to use for logging in. If None, the default project
            is used.
        :param service: The service to use for logging in. If None, the first service in
            the list is used.
        :param verify: Bool or string. If False, no verification of SSL certificates
            is done when connecting via HTTPS. If it is a string, it should be the
            path to the CA_BUNDLE file or directory with certificates of trusted CAs-
            If true, the built-in list of trusted CAs will be used.
        """
        self.address = address.rstrip("/")  # Remove trailing slash if present
        self.username = getpass.getuser()
        self.verify = verify
        if service is None:
            logger.debug("No service specified, getting service from Empower")
            try:
                response = requests.get(
                    self.address + "/authentication/db-service-list",
                    timeout=10,
                    verify=self.verify,
                )
            except requests.exceptions.Timeout as e:
                timeout_string = f"Getting service from {self.address} timed out"
                print(timeout_string)
                logger.error(timeout_string)
                raise requests.exceptions.Timeout(timeout_string) from e
            self.service = response.json()["results"][0]["netServiceName"]
            # If no service is specified, use the first one in the list
        else:
            self.service = service
        self.project = project
        self.session_id = None
        self.token = None
        self.default_get_timeout = 20
        self.default_post_timeout = 40

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
            response = requests.post(
                self.address + "/authentication/login",
                json=body,
                timeout=600,
                verify=self.verify,
            )
        except requests.exceptions.Timeout as e:
            timeout_string = (
                f"Login to {self.address} with username = {self.username} timed out"
            )
            logger.error(timeout_string)
            raise requests.exceptions.Timeout(timeout_string) from e
        self.raise_for_status(response)
        self.token = response.json()["results"][0]["token"]
        self.session_id = response.json()["results"][0]["id"]
        logger.debug("Login successful, keeping token")

    def logout(self) -> None:
        """Log out of Empower."""
        if self.session_id is None:
            logger.debug("No session ID, no need to log out")
            return
        logger.debug("Logging out of Empower")
        response = requests.delete(
            self.address + "/authentication/logout?sessionInfoID=" + self.session_id,
            headers=self.authorization_header,
            timeout=self.default_post_timeout,
            verify=self.verify,
        )
        if response.status_code == 404:
            logger.debug(
                "Logout no necessary, session already expired or were logged out."
            )
        else:
            self.raise_for_status(response)
        self.session_id = None
        logger.debug("Logout successful")

    def _requests_wrapper(
        self, method: str, endpoint: str, body: Optional[dict], timeout
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Wrapper for requests.

        :param method: The method to use.
        :param endpoint: The endpoint to use.
        :param body: The body to use.
        :param timeout: The timeout to use.

        :return: The results and message from the response.
        """

        def _request_with_timeout(method, endpoint, header, body, timeout, verify):
            try:
                return requests.request(
                    method,
                    endpoint,
                    json=body,
                    headers=header,
                    timeout=timeout,
                    verify=verify,
                )
            except requests.exceptions.Timeout as e:
                timeout_string = f"{method}ing {body} to {endpoint} timed out"
                print(timeout_string)
                logger.error(timeout_string)
                raise requests.exceptions.Timeout(timeout_string) from e

        endpoint = endpoint.lstrip("/")  # Remove leading slash if present
        address = self.address + "/" + endpoint
        # Add slash between address and endpoint
        logger.debug("%sing %s to %s", method, body, address)
        response = _request_with_timeout(
            method, address, self.authorization_header, body, timeout, self.verify
        )
        if response.status_code == 401:
            logger.debug("Token expired, logging in again")
            self.login()
            response = _request_with_timeout(
                method, address, self.authorization_header, body, timeout, self.verify
            )
        logger.debug("Got response %s from %s", response.text, address)
        self.raise_for_status(response)
        return (
            response.json().get("results", None),
            response.json().get("message", None),
        )  # Safely getting the results and message from the response, if they don't
        # exist, return None

    def get(
        self, endpoint: str, timeout: Optional[int] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Get data from Empower.

        :param endpoint: The endpoint to get data from.
        :param timeout: The timeout to use. If None, the default timeout is used.

        :return: The results and message from the response.
        """
        if not timeout:
            timeout = self.default_get_timeout
        else:
            logger.debug("Timeout changed from default value to %s", timeout)
            print(
                f"Get call to endpoint {endpoint} could be slow, "
                f"timeout is set to {timeout} seconds"
            )
        logger.debug("Getting data from %s with timeout %s", endpoint, timeout)
        response = self._requests_wrapper(
            method="get", endpoint=endpoint, body=None, timeout=timeout
        )
        if response[1]:
            logger.debug("Got message from Empower %s", response[1])
        return response

    def post(
        self, endpoint: str, body: dict, timeout: Optional[int] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Post data to Empower.

        :param endpoint: The endpoint to post data to.
        :param body: The data to post.
        :param timeout: The timeout to use. If None, the default timeout is used.

        :return: The results and message from the response.
        """
        if not timeout:
            timeout = self.default_get_timeout
        else:
            logger.debug("Timeout changed from default value to %s", timeout)
            print(
                f"Post call to endpoint {endpoint} could be slow, "
                f"timeout is set to {timeout} seconds"
            )
        logger.debug("Posting data %s to %s with timeout %s", body, endpoint, timeout)
        response = self._requests_wrapper(
            method="post", endpoint=endpoint, body=body, timeout=timeout
        )
        if response[1]:
            logger.debug("Got message from Empower %s", response[1])
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

    @staticmethod
    def raise_for_status(response: requests.Response):
        """
        Raise an error if the response is not ok. This error includes the message from
        Empower, as opposed to the raise_for_status() method of requests.
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            body = response.json()
            if "message" in body and "id" in body:
                error = requests.exceptions.HTTPError(
                    f"HTTP error {response.status_code} "
                    f"with message '{response.json()['message']}' "
                    f"and ID {response.json()['id']}"
                )
            elif "errors" in body:
                error = requests.exceptions.HTTPError(
                    f"HTTP error {response.status_code} "
                    f"with errors '{response.json()['errors']}'"
                )
            raise error from None
