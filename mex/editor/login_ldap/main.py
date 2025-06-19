import reflex as rx

from mex.editor.components import login_form
from mex.editor.login_ldap.state import LoginLdapState


def index() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginLdapState)
