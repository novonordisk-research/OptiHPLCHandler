import logging
from typing import List

from .empower_api_core import EmpowerConnection

logger = logging.getLogger(__name__)


class EmpowerSession:
    def __init__(
        self,
        project: str,
        address: str,
        service: str = None,
        username: str = None,
        password: str = None,
    ):
        self.project = project
        self.address = address
        self.service = service
        self.username = username
        self.password = password

    def __enter__(self):
        """
        Used for entering the context manager. Right now EmpowerSession is
        designed to be used with context manager.
        """
        if not self.username:
            raise ValueError("username must be set")

        if not self.password:
            raise ValueError("password must be set")

        self.connection = EmpowerConnection(
            project=self.project,
            address=self.address,
            service=self.service,
            username=self.username,
        )

        # Because Empower connection currently is slow the timeout is increased
        self.connection.default_get_timeout = 120
        self.connection.default_post_timeout = 120

        self.connection.login(
            username=self.username,
            password=self.password,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.logout()

    def GetSessionInfoes(self) -> List[str]:
        """
        Returns a list of all sessions that the user currently have.
        """
        return self.connection.get(endpoint="authentication/session-infoes")[0]

    def LogoutAllSessions(self):
        """
        Logout all sessions.
        """
        allSessions = self.GetSessionInfoes()
        for session in allSessions:
            self.connection.session_id = session["id"]
            self.connection.logout()
