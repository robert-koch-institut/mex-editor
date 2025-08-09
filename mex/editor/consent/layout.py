import reflex as rx

from mex.editor.layout import app_logo
from mex.editor.state import State


def nav_bar() -> rx.Component:
    """Return a consent navigation bar component."""
    return rx.vstack(
        rx.box(
            style={
                "height": "var(--space-6)",
                "width": "100%",
                "backdropFilter": " var(--backdrop-filter-panel)",
            },
        ),
        rx.card(
            rx.hstack(
                app_logo(),
                rx.divider(orientation="vertical", size="2"),
                rx.card(
                    rx.text(
                        "Informed Consent",
                        size="1",
                    ),
                ),
                rx.spacer(),
                rx.color_mode.button(),
                justify="between",
                align_items="center",
            ),
            size="2",
            custom_attrs={"data-testid": "nav-bar"},
            style={
                "width": "100%",
                "marginTop": "calc(-1 * var(--base-card-border-width))",
            },
        ),
        spacing="0",
        style={
            "maxWidth": "var(--app-max-width)",
            "minWidth": "var(--app-min-width)",
            "position": "fixed",
            "top": "0",
            "width": "100%",
            "zIndex": "1000",
        },
    )


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with the consent navigation bar and given children."""
    return rx.cond(
        State.user_ldap,
        rx.center(
            nav_bar(),
            rx.hstack(
                *children,
                style={
                    "maxWidth": "var(--app-max-width)",
                    "minWidth": "var(--app-min-width)",
                    "padding": "calc(var(--space-6) * 4) var(--space-6) var(--space-6)",
                    "width": "100%",
                },
                custom_attrs={"data-testid": "page-body"},
            ),
            style={
                "--app-max-width": "calc(1480px * var(--scaling))",
                "--app-min-width": "calc(800px * var(--scaling))",
            },
        ),
        rx.center(
            rx.spinner(size="3"),
            style={"marginTop": "40vh"},
        ),
    )
