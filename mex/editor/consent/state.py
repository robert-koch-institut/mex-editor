import reflex as rx
from reflex.event import EventSpec

from mex.common.ldap.connector import LDAPConnector
from mex.editor.state import State


class ConsentState(State):
    """State for the consent component."""

    display_name: rx.Field[str | None] = rx.field(None)

    @rx.event
    def load_user(self) -> EventSpec | None:
        """Set the stem type to a default."""
        connector = LDAPConnector.get()
        if not self.user_ldap:
            self.target_path_after_login = str(self.router.url)
            return rx.redirect("/login-ldap")
        person = connector.get_person(sAMAccountName=self.user_ldap.name)
        self.display_name = person.displayName
        return None
