import reflex as rx

from mex.editor.layout import app_logo
from mex.editor.login.state import LoginLdapState, LoginMExState


def login_user(state: type[LoginLdapState | LoginMExState]) -> rx.Component:
    """Return a form field for the user name."""
    return rx.vstack(
        rx.text(state.label_username),
        rx.input(
            autofocus=True,
            name="username",
            on_change=state.set_username,
            placeholder=state.label_username,
            size="3",
            tab_index=1,
            style=rx.Style(width="100%"),
            custom_attrs={"data-testid": "input-username"},
        ),
        style=rx.Style(width="100%"),
    )


def login_password(state: type[LoginLdapState | LoginMExState]) -> rx.Component:
    """Return a form field for the password."""
    return rx.vstack(
        rx.text(state.label_password),
        rx.input(
            on_change=state.set_password,
            name="password",
            placeholder=state.label_password,
            size="3",
            tab_index=2,
            type="password",
            style=rx.Style(width="100%"),
            custom_attrs={"data-testid": "input-password"},
        ),
        style=rx.Style(width="100%"),
    )


def login_button(state: type[LoginLdapState | LoginMExState]) -> rx.Component:
    """Return a submit button for the login form."""
    return rx.hstack(
        rx.spacer(),
        rx.button(
            state.label_button_login,
            size="3",
            tab_index=3,
            style=rx.Style(
                padding="0 var(--space-6)",
                marginTop="var(--space-4)",
            ),
            custom_attrs={"data-testid": "login-button"},
            type="submit",
        ),
        style=rx.Style(width="100%"),
    )


def login_form(state: type[LoginLdapState | LoginMExState]) -> rx.Component:
    """Return a login form."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.hstack(
                    app_logo(),
                    rx.spacer(spacing="4"),
                    rx.button(
                        rx.icon("sun_moon"),
                        variant="ghost",
                        style=rx.Style(marginTop="0"),
                        on_click=rx.toggle_color_mode,
                    ),
                    style=rx.Style(width="100%"),
                ),
                rx.divider(size="4"),
                rx.form(
                    rx.vstack(
                        login_user(state),
                        login_password(state),
                        login_button(state),
                        style=rx.Style(width="100%"),
                    ),
                    on_submit=state.login,
                    spacing="4",
                ),
            ),
            style=rx.Style(
                width="calc(340px * var(--scaling))",
                padding="var(--space-4)",
                top="20vh",
            ),
            custom_attrs={"data-testid": "login-card"},
        )
    )


def ldap_login() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginLdapState)


def mex_login() -> rx.Component:
    """Return the index for the login component."""
    return login_form(LoginMExState)
