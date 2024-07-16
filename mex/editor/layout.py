from collections import defaultdict
from typing import Literal

import reflex as rx

from mex.editor.state import State

Header = Literal["search"] | Literal["edit"] | Literal["merge"]


def user_menu() -> rx.Component:
    """Return a user menu button with an icon indicating their access rights."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.cond(
                    State.user.write_access,  # type: ignore[union-attr]
                    rx.icon(tag="user_round_cog"),
                    rx.icon(tag="user_round"),
                ),
                variant="ghost",
                style={"marginTop": "0"},
            ),
        ),
        rx.menu.content(
            rx.menu.item(
                State.user.name,  # type: ignore[union-attr]
                disabled=True,
            ),
            rx.menu.separator(),
            rx.menu.item(
                "Logout",
                on_select=State.logout,
            ),
        ),
    )


def nav_links(heading: Header) -> list[rx.Component]:
    """Return a list of navigation links with the current heading highlighted."""
    should_underline = defaultdict(lambda: "none", {heading: "always"})
    return [
        rx.link(
            "Search",
            href="/",
            underline=should_underline["search"],
            padding="0.2em",
        ),
        rx.link(
            "Edit",
            href="/item/123",
            underline=should_underline["edit"],
            padding="0.2em",
        ),
        rx.link(
            "Merge",
            href="/merge",
            underline=should_underline["merge"],
            padding="0.2em",
        ),
    ]


def nav_bar(heading: Header) -> rx.Component:
    """Return a navigation bar component."""
    return rx.hstack(
        rx.icon("file-pen-line", size=28),
        rx.heading("MEx Editor", weight="medium"),
        rx.divider(orientation="vertical", size="2"),
        *nav_links(heading),
        rx.divider(orientation="vertical", size="2"),
        user_menu(),
        rx.spacer(),
        rx.color_mode.button(),
        id="navbar",
        padding="1em",
        position="fixed",
        style=rx.style.Style(background="var(--accent-4)"),
        top="0px",
        width="100%",
        z_index="1000",
    )


def page(heading: Header, *children: str | rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    return rx.fragment(
        nav_bar(heading),
        rx.vstack(
            *children,
            justify="center",
            min_height="85vh",
            margin="4em 1em 1em",
            spacing="5",
        ),
    )
