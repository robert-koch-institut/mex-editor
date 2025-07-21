from base64 import b64encode

import reflex as rx
from reflex.event import EventSpec

from mex.editor.security import (
    has_read_access_mex,
    has_write_access_ldap,
    has_write_access_mex,
)
from mex.editor.state import State, User


class LoginLdapState(State):
    """State management for the login page."""

    username: rx.Field[str] = rx.field("")
    password: rx.Field[str] = rx.field("")

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
        write_access = has_write_access_ldap(self.username, self.password)
        if write_access:
            encoded = b64encode(f"{self.username}:{self.password}".encode("ascii"))
            self.user_ldap = User(
                name=self.username,
                authorization=f"Basic {encoded.decode('ascii')}",
                write_access=write_access,
            )
            if self.target_path_after_login:
                target_path_after_login = self.target_path_after_login
            else:
                target_path_after_login = "/"
            self.reset()  # reset username/password
            return rx.redirect(target_path_after_login)
        return rx.window_alert("Invalid credentials.")


class LoginMExState(State):
    """State management for the login page."""

    username: rx.Field[str] = rx.field("")
    password: rx.Field[str] = rx.field("")

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
            encoded = b64encode(f"{self.username}:{self.password}".encode("ascii"))
            self.user_mex = User(
                name=self.username,
                authorization=f"Basic {encoded.decode('ascii')}",
                write_access=write_access,
            )
            if self.target_path_after_login:
                target_path_after_login = self.target_path_after_login
            else:
                target_path_after_login = "/"
            self.reset()  # reset username/password
            return rx.redirect(target_path_after_login)
        return rx.window_alert("Invalid credentials.")
