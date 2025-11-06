import reflex as rx

from mex.editor.consent.state import ConsentState
from mex.editor.layout import nav_bar
from mex.editor.state import State


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with the consent navigation bar and given children."""
    return rx.cond(
        State.user_ldap,
        rx.center(
            nav_bar(ConsentState.get_consent_nav_items()),
            rx.hstack(
                *children,
                style=rx.Style(
                    maxWidth="var(--app-max-width)",
                    minWidth="var(--app-min-width)",
                    padding="calc(var(--space-6) * 4) var(--space-6) var(--space-6)",
                    width="100%",
                ),
                custom_attrs={"data-testid": "page-body"},
            ),
            style=rx.Style(
                {
                    "--app-max-width": "calc(1480px * var(--scaling))",
                    "--app-min-width": "calc(800px * var(--scaling))",
                }
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(marginTop="40vh"),
        ),
    )
