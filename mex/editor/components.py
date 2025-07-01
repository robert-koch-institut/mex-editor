from typing import cast

import reflex as rx

from mex.editor.layout import app_logo
from mex.editor.rules.models import EditorValue


def render_identifier(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.skeleton(
        rx.link(
            cast("rx.vars.StringVar", value.text) | "Loading ...",
            href=value.href,
            high_contrast=True,
            role="link",
        ),
        loading=~cast("rx.vars.StringVar", value.text),
    )


def render_external_link(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable external link that opens in a new tab."""
    return rx.link(
        value.text,
        href=value.href,
        high_contrast=True,
        is_external=True,
        role="link",
    )


def render_link(value: EditorValue) -> rx.Component:
    """Render an editor value as an internal or external link."""
    return rx.cond(
        value.identifier,
        render_identifier(value),
        render_external_link(value),
    )


def render_span(text: str | None) -> rx.Component:
    """Render a generic span with the given text."""
    return rx.text(
        text,
        as_="span",
    )


def render_text(value: EditorValue) -> rx.Component:
    """Render an editor value as a text span."""
    return rx.skeleton(
        render_span(cast("rx.vars.StringVar", value.text) | "Loading ..."),
        loading=~cast("rx.vars.StringVar", value.text),
    )


def render_badge(text: str | None) -> rx.Component:
    """Render a generic badge with the given text."""
    return rx.badge(
        text,
        radius="large",
        variant="soft",
        color_scheme="gray",
        style={"margin": "auto 0"},
    )


def render_value(value: EditorValue) -> rx.Component:
    """Render a single editor value."""
    return rx.hstack(
        rx.cond(
            value.href,
            render_link(value),
            render_text(value),
        ),
        rx.cond(
            value.badge,
            render_badge(value.badge),
        ),
        spacing="1",
    )


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
            style={"width": "80%"},
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
            style={"width": "80%"},
        ),
        style={"width": "100%"},
    )


def login_button() -> rx.Component:
    """Return a submit button for the login form."""
    return rx.button(
        "Login",
        size="3",
        tab_index=3,
        style={
            "padding": "0 var(--space-6)",
            "marginTop": "var(--space-4)",
        },
        custom_attrs={"data-testid": "login-button"},
        type="submit",
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
                style={
                    "width": "calc(400px * var(--scaling))",
                    "padding": "var(--space-4)",
                    "top": "20vh",
                },
                variant="classic",
                custom_attrs={"data-testid": "login-card"},
            ),
        )
    )
