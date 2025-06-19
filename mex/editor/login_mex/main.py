import reflex as rx

from mex.editor.components import login_form
from mex.editor.login_mex.state import LoginMexState


def index() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginMexState)
