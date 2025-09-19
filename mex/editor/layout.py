from typing import TYPE_CHECKING, cast

import reflex as rx

from mex.editor.locale_service import LocaleService
from mex.editor.state import NavItem, State

if TYPE_CHECKING:
    from mex.editor.models import User

locale_service = LocaleService.get()


def user_button() -> rx.Component:
    """Return a user button with an icon that indicates their access rights."""
    return rx.button(
        rx.cond(
            cast("User", State.user_mex).write_access,
            rx.icon(tag="user_round_cog"),
            rx.icon(tag="user_round"),
        ),
        variant="ghost",
        style={"marginTop": "0"},
    )


def user_menu() -> rx.Component:
    """Return a user menu with a trigger, the user's name and a logout button."""
    return rx.menu.root(
        rx.menu.trigger(
            user_button(),
            custom_attrs={"data-testid": "user-menu"},
        ),
        rx.menu.content(
            rx.menu.item(cast("User", State.user_mex).name, disabled=True),
            rx.menu.separator(),
            rx.menu.item(
                "Logout",
                on_select=State.logout,
                custom_attrs={"data-testid": "logout-button"},
            ),
        ),
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        on_click=State.navigate(item.raw_path),
        underline=item.underline,
        class_name="nav-item",
        custom_attrs={"data-href": item.raw_path},
    )


def app_logo() -> rx.Component:
    """Return the app logo with icon and label."""
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.icon(
                    tag="circuit-board",
                    size=28,
                ),
                rx.heading(
                    "MEx Editor",
                    weight="medium",
                    style={"userSelect": "none"},
                ),
                custom_attrs={"data-testid": "app-logo"},
            )
        ),
        rx.hover_card.content(
            rx.vstack(
                rx.code(f"mex-editor=={State.editor_version}", variant="outline"),
                rx.code(f"mex-backend=={State.backend_version}", variant="outline"),
            ),
        ),
        open_delay=500,
    )


def language_switcher() -> rx.Component:
    """Render a language switcher."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                State.current_locale,
                style={
                    "background": "transparent",
                    "color": "inherit",
                    "z_index": "20",
                    ":hover": {"cursor": "pointer"},
                },
            ),
            custom_attrs={"data-testid": "language-switcher"},
        ),
        rx.menu.content(
            *[
                rx.menu.item(
                    rx.text(locale.label),
                    on_click=State.change_locale(locale.id),
                    custom_attrs={
                        "data-testid": f"language-switcher-menu-item-{locale.id}"
                    },
                )
                for locale in locale_service.get_available_locales()
            ]
        ),
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
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
                rx.hstack(
                    rx.foreach(State.nav_items, nav_link),
                    justify="start",
                    spacing="4",
                ),
                rx.divider(orientation="vertical", size="2"),
                user_menu(),
                rx.spacer(),
                language_switcher(),
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


def navigate_away_dialog() -> rx.Component:
    """Render a dialog that informs the user about unsaved changes on the page.

    If the dialog is dismissed navigatio is stopped and the user stays on the page
    ; otherwise navigate away.
    """
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Unsaved changes"),
            rx.alert_dialog.description(
                "There are unsaved changes on the page. If u navigate away "
                "these changes will be lost. Do you want to navigate anyway?",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancel", on_click=State.close_navigate_dialog)
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Discard changes",
                        color_scheme="red",
                        on_click=[
                            State.close_navigate_dialog,
                            State.set_current_page_has_changes(False),
                            State.navigate(State.navigate_target),
                        ],
                    )
                ),
                spacing="3",
            ),
        ),
        open=State.navigate_dialog_open,
    )


def page_leave_js() -> rx.Component:
    """Render page leave java script import.

    Returns:
        rx.Component: The script component refrencing the
        '/page-leave-warn-unsaved-changes.js'
    """
    return rx.script(src="/page-leave-warn-unsaved-changes.js")


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    return rx.cond(
        State.user_mex,
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
            navigate_away_dialog(),
            page_leave_js(),
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
