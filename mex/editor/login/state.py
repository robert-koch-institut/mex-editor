from base64 import b64encode

import reflex as rx
from reflex.event import EventSpec

from mex.editor.security import has_read_access, has_write_access
from mex.editor.state import State, User


class LoginState(State):
    """State management for the login page."""

    username: str
    password: str

    def login(self) -> EventSpec:
        """Log in a user."""
        read_access = has_read_access(self.username, self.password)
        write_access = has_write_access(self.username, self.password)
        if read_access:
            encoded = b64encode(f"{self.username}:{self.password}".encode("ascii"))
            self.user = User(
                name=self.username,
                authorization=f"Basic {encoded.decode('ascii')}",
                write_access=write_access,
            )
            if self.target_path_after_login:
                return rx.redirect(self.target_path_after_login)
            return rx.redirect("/")
        return rx.window_alert("Invalid credentials.")
