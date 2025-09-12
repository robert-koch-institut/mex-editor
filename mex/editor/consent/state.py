from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec

from mex.common.ldap.connector import LDAPConnector
from mex.editor.state import State


class ConsentState(State):
    """State for the consent component."""

    display_name: str | None = None

    @rx.event
    def load_user(self) -> Generator[EventSpec, None, None]:
        """Set the stem type to a default."""
        connector = LDAPConnector.get()
        if not self.user_ldap:
            self.target_path_after_login = self.router.page.raw_path
            yield rx.redirect("/login-ldap")
        else:
            person = connector.get_person(sam_account_name=self.user_ldap.name)
            self.display_name = person.displayName
