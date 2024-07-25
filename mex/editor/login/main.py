import reflex as rx

from mex.editor.layout import mex_editor_logo
from mex.editor.login.state import LoginState


def login_form() -> rx.Component:
    """Return a vertical stack of login form components."""
    return rx.vstack(
        rx.vstack(
            rx.text("Username"),
            rx.input(
                autofocus=True,
                on_change=LoginState.set_username,
                placeholder="Username",
                size="3",
                tab_index=1,
                style={"width": "80%"},
            ),
            style={"width": "100%"},
        ),
        rx.vstack(
            rx.text("Password"),
            rx.input(
                on_change=LoginState.set_password,
                placeholder="Password",
                size="3",
                tab_index=2,
                type="password",
                style={"width": "80%"},
            ),
            style={"width": "100%"},
        ),
        rx.button(
            "Log in",
            on_click=LoginState.login,
            size="3",
            tab_index=3,
            width="5em",
        ),
    )


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                mex_editor_logo(),
                rx.divider(size="4"),
                login_form(),
                spacing="4",
            ),
            top="20vh",
            width="400px",
            variant="classic",
        ),
    )
