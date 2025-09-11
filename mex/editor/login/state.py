from urllib.parse import urljoin

import reflex as rx
import requests
from reflex.event import EventSpec
from requests import RequestException

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.settings import BaseSettings
from mex.editor.security import (
    has_read_access_mex,
    has_write_access_mex,
)
from mex.editor.state import State, User


class LoginLdapState(State):
    """State management for the login page."""

    username: str
    password: str

    @rx.event
    def set_username(self, username: str) -> None:
        """Set the username."""
        self.username = username

    @rx.event
    def set_password(self, password: str) -> None:
        """Set the password."""
        self.password = password

    @rx.event
    def login(self) -> EventSpec:
        """Login a user."""
        settings = BaseSettings.get()
        url = urljoin(
            str(settings.backend_api_url),
            f"{BackendApiConnector.API_VERSION}/merged-person-from-login",
        )  # uses endpoint without setting header

        try:
            response = requests.post(
                url, auth=(self.username, self.password), timeout=10
            )
        except RequestException:
            return rx.window_alert("Cannot reach backend. Please try again later.")
        if response:
            self.user_ldap = User(
                name=self.username,
                write_access=True,
            )
            self.merged_login_person = response.json()
            target_path_after_login = self.target_path_after_login or "/"
            self.reset()  # reset username/password
            return rx.redirect(target_path_after_login)
        return rx.window_alert("Invalid credentials.")


class LoginMExState(State):
    """State management for the login page."""

    username: str
    password: str

    @rx.event
    def set_username(self, username: str) -> None:
        """Set the username."""
        self.username = username

    @rx.event
    def set_password(self, password: str) -> None:
        """Set the password."""
        self.password = password

    @rx.event
    def login(self) -> EventSpec:
        """Login a user."""
        read_access = has_read_access_mex(self.username, self.password)
        write_access = has_write_access_mex(self.username, self.password)
        if read_access:
            self.user_mex = User(
                name=self.username,
                write_access=write_access,
            )
            if self.target_path_after_login:
                target_path_after_login = self.target_path_after_login
            else:
                target_path_after_login = "/"
            self.reset()  # reset username/password
            return rx.redirect(target_path_after_login)
        return rx.window_alert("Invalid credentials.")
