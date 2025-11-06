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
            rx.icon("user_round_cog"),
            rx.icon("user_round"),
        ),
        variant="ghost",
        style=rx.Style(marginTop="0"),
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
            align="end",
        ),
    )


def language_switcher() -> rx.Component:
    """Render a language switcher."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                State.current_locale,
                style=rx.Style(fontWeight="var(--font-weight-medium)"),
                variant="ghost",
            ),
            custom_attrs={"data-testid": "language-switcher"},
        ),
        rx.menu.content(
            rx.foreach(
                locale_service.get_available_locales(),
                lambda locale: rx.menu.item(
                    rx.text(locale.label),
                    on_click=State.change_locale(locale.id),  # type: ignore[misc]
                    custom_attrs={
                        "data-testid": f"language-switcher-menu-item-{locale.id}"
                    },
                ),
            )
        ),
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        on_click=State.navigate(item.raw_path),  # type: ignore[misc]
        underline=item.underline,  # type: ignore[arg-type]
        class_name="nav-item",
        custom_attrs={"data-href": item.raw_path},
    )


def app_logo() -> rx.Component:
    """Return the app logo with icon and label."""
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.icon("circuit-board", size=28),
                rx.heading(
                    "MEx Editor",
                    weight="medium",
                    style=rx.Style(userSelect="none"),
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


def nav_bar(nav_items_source: list[NavItem] | None = None) -> rx.Component:
    """Return a navigation bar component."""
    nav_items_to_use = (
        nav_items_source if nav_items_source is not None else State.nav_items
    )
    return rx.vstack(
        rx.box(
            style=rx.Style(
                height="var(--space-6)",
                width="100%",
                backdropFilter="var(--backdrop-filter-panel)",
            ),
        ),
        rx.card(
            rx.hstack(
                app_logo(),
                rx.divider(orientation="vertical", size="2"),
                rx.hstack(
                    rx.foreach(nav_items_to_use, nav_link),
                    justify="start",
                    spacing="4",
                ),
                rx.spacer(),
                rx.hstack(
                    language_switcher(),
                    user_menu(),
                    rx.button(
                        rx.icon("sun_moon"),
                        variant="ghost",
                        style=rx.Style(marginTop="0"),
                        on_click=rx.toggle_color_mode,
                    ),
                    style=rx.Style(alignItems="center"),
                    spacing="4",
                ),
                justify="between",
                align_items="center",
            ),
            size="2",
            custom_attrs={"data-testid": "nav-bar"},
            style=rx.Style(
                width="100%",
                marginTop="calc(-1 * var(--base-card-border-width))",
            ),
        ),
        spacing="0",
        style=rx.Style(
            maxWidth="var(--app-max-width)",
            minWidth="var(--app-min-width)",
            position="fixed",
            top="0",
            width="100%",
            zIndex="1000",
        ),
    )


def navigate_away_dialog() -> rx.Component:
    """Render a dialog that informs the user about unsaved changes on the page.

    If the dialog is dismissed navigation is stopped and the user stays on the page;
    otherwise navigate away.
    """
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Unsaved changes"),
            rx.alert_dialog.description(
                "There are unsaved changes on the page. If you navigate away "
                "these changes will be lost. Do you want to navigate anyway?",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Stay here",
                        color_scheme="gray",
                        on_click=State.close_navigate_dialog,
                    )
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Navigate away",
                        color_scheme="tomato",
                        on_click=[
                            State.close_navigate_dialog,
                            State.set_current_page_has_changes(False),  # type: ignore[misc]
                            State.navigate(State.navigate_target),  # type: ignore[misc]
                        ],
                    )
                ),
                spacing="3",
                style=rx.Style(marginTop="1rem"),
                justify="end",
            ),
        ),
        open=State.navigate_dialog_open,
    )


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    return rx.cond(
        State.user_mex,
        rx.center(
            nav_bar(),
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
            navigate_away_dialog(),
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
