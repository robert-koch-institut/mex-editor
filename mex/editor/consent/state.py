import reflex as rx
from reflex.event import EventSpec

from mex.common.ldap.connector import LDAPConnector
from mex.editor.state import State


class ConsentState(State):
    """State for the consent component."""

    display_name: str | None = None

    @rx.event
    def load_user(self) -> EventSpec | None:
        """Set the stem type to a default."""
        connector = LDAPConnector.get()
        if not self.ldap_user:
            self.target_path_after_login = self.router.page.raw_path
            return rx.redirect("/login-ldap")
        person = connector.get_person(sAMAccountName=self.ldap_user.name)
        self.display_name = person.displayName
        return None
