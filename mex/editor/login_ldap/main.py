import reflex as rx

from mex.editor.layout import app_logo
from mex.editor.login_ldap.state import LoginState


def login_user() -> rx.Component:
    """Return a form field for the user name."""
    return rx.vstack(
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
    )


def login_password() -> rx.Component:
    """Return a form field for the password."""
    return rx.vstack(
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
    )


def login_button() -> rx.Component:
    """Return a submit button for the login form."""
    return rx.button(
        "Login",
        on_click=LoginState.login,
        size="3",
        tab_index=3,
        style={
            "padding": "0 var(--space-6)",
            "marginTop": "var(--space-4)",
        },
        custom_attrs={"data-testid": "login-button"},
    )


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.hstack(
                    app_logo(),
                    rx.spacer(spacing="4"),
                    rx.color_mode.button(),
                    style={"width": "100%"},
                ),
                rx.divider(size="4"),
                rx.vstack(
                    login_user(),
                    login_password(),
                    login_button(),
                    style={"width": "100%"},
                ),
                spacing="4",
            ),
            style={
                "width": "calc(400px * var(--scaling))",
                "padding": "var(--space-4)",
                "top": "20vh",
            },
            variant="classic",
            custom_attrs={"data-testid": "login-card"},
        ),
    )
