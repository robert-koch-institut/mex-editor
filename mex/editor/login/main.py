import reflex as rx

from mex.editor.layout import app_logo
from mex.editor.login.state import LoginLdapState, LoginMExState


def login_user(state: type[rx.State]) -> rx.Component:
    """Return a form field for the user name."""
    return rx.vstack(
        rx.text("Username"),
        rx.input(
            autofocus=True,
            name="username",
            on_change=state.set_username,
            placeholder="Username",
            size="3",
            tab_index=1,
            style={"width": "100%"},
        ),
        style={"width": "100%"},
    )


def login_password(state: type[rx.State]) -> rx.Component:
    """Return a form field for the password."""
    return rx.vstack(
        rx.text("Password"),
        rx.input(
            on_change=state.set_password,
            name="password",
            placeholder="Password",
            size="3",
            tab_index=2,
            type="password",
            style={"width": "100%"},
        ),
        style={"width": "100%"},
    )


def login_button() -> rx.Component:
    """Return a submit button for the login form."""
    return rx.hstack(
        rx.spacer(),
        rx.button(
            "Login",
            size="3",
            tab_index=3,
            style={
                "padding": "0 var(--space-6)",
                "marginTop": "var(--space-4)",
            },
            custom_attrs={"data-testid": "login-button"},
            type="submit",
        ),
        style={"width": "100%"},
    )


def login_form(state: type[rx.State]) -> rx.Component:
    """Return a login form."""
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
                rx.form(
                    rx.vstack(
                        login_user(state),
                        login_password(state),
                        login_button(),
                        style={"width": "100%"},
                    ),
                    on_submit=state.login,
                    spacing="4",
                ),
            ),
            style={
                "width": "calc(340px * var(--scaling))",
                "padding": "var(--space-4)",
                "top": "20vh",
            },
            custom_attrs={"data-testid": "login-card"},
        )
    )


def ldap_login() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginLdapState)


def mex_login() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginMExState)
