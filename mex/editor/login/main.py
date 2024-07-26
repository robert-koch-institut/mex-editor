import reflex as rx

from mex.editor.login.state import LoginState


def login_form() -> list[rx.Component]:
    """Return the login form components."""
    return [
        rx.vstack(
            rx.text("Username"),
            rx.input(
                autofocus=True,
                on_change=LoginState.set_username,
                placeholder="Username",
                size="3",
                tab_index=1,
            ),
        ),
        rx.vstack(
            rx.text("Password"),
            rx.input(
                on_change=LoginState.set_password,
                placeholder="Password",
                size="3",
                tab_index=2,
                type="password",
            ),
        ),
        rx.button(
            "Log in",
            on_click=LoginState.login,
            size="3",
            tab_index=3,
            width="5em",
        ),
    ]


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "file-pen-line",
                        size=28,
                    ),
                    rx.heading(
                        "MEx Editor",
                        weight="medium",
                    ),
                ),
                rx.divider(size="4"),
                *login_form(),
                spacing="4",
            ),
            top="4em",
            width="400px",
        )
    )
