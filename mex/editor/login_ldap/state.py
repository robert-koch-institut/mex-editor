from base64 import b64encode

import reflex as rx
from reflex.event import EventSpec

from mex.editor.security import has_write_access_ldap
from mex.editor.state import State, User


class LoginLdapState(State):
    """State management for the login page."""

    username: str
    password: str

    @rx.event
    def login(self) -> EventSpec:
        """Login a user."""
        write_access = has_write_access_ldap(self.username, self.password)
        if write_access:
            encoded = b64encode(f"{self.username}:{self.password}".encode("ascii"))
            self.ldap_user = User(
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
