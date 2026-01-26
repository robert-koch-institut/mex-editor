from collections.abc import Generator
from urllib.parse import urljoin

import reflex as rx
import requests
from reflex.event import EventSpec
from requests import RequestException

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.settings import BaseSettings
from mex.editor.exceptions import escalate_error
from mex.editor.label_var import label_var
from mex.editor.models import MergedLoginPerson
from mex.editor.security import has_read_access_mex, has_write_access_mex
from mex.editor.state import State, User


class LoginState(State):
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

    @label_var(label_id="login.username")
    def label_username(self) -> None:
        """Label for username."""

    @label_var(label_id="login.password")
    def label_password(self) -> None:
        """Label for password."""

    @label_var(label_id="login.button_login")
    def label_button_login(self) -> None:
        """Label for button_login."""

    @label_var(label_id="login.invalid_credentials")
    def label_invalid_credentials(self) -> None:
        """Label for invalid_credentials."""


class LoginLdapState(LoginState):
    """State management for the login page."""

    @rx.event
    def login(self) -> Generator[EventSpec, None, None]:
        """Login a user."""
        settings = BaseSettings.get()
        url = urljoin(
            str(settings.backend_api_url),
            f"{BackendApiConnector.API_VERSION}/merged-person-from-login",
        )  # stopgap: MX-2083

        try:
            response = requests.post(
                url, auth=(self.username, self.password), timeout=10
            )
        except RequestException as exc:
            yield from escalate_error(
                "backend", "Cannot reach backend. Please try again later.", exc
            )
            return
        if response:
            self.user_ldap = User(
                name=self.username,
                write_access=True,
            )
            response_user = response.json()
            self.merged_login_person = MergedLoginPerson(
                identifier=response_user["identifier"],
                full_name=response_user["fullName"],
                email=response_user["email"],
                orcid_id=response_user["orcidId"],
            )
            target_path_after_login = self.target_path_after_login or "/"
            self.reset()  # reset username/password
            yield rx.redirect(target_path_after_login)
        else:
            yield rx.toast.error(
                self.label_invalid_credentials, class_name="editor-toast"
            )


class LoginMExState(LoginState):
    """State management for the login page."""

    @rx.event
    def login(self) -> Generator[EventSpec, None, None]:
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
            yield rx.redirect(target_path_after_login)
        else:
            yield rx.toast.error(
                self.label_invalid_credentials, class_name="editor-toast"
            )
