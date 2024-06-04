from collections import defaultdict
from typing import Literal

import reflex as rx

Header = Literal["search"] | Literal["edit"] | Literal["merge"]


def navbar(heading: Header) -> rx.Component:
    """Return a navigation bar component."""
    should_underline = defaultdict(lambda: "none", {heading: "always"})
    return rx.hstack(
        rx.icon("file-pen-line", size=28),
        rx.heading("MEx Editor", weight="medium"),
        rx.divider(orientation="vertical", size="2"),
        rx.link(
            "Search", href="/", underline=should_underline["search"], padding="0.2em"
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
        rx.spacer(),
        rx.color_mode.button(),
        id="navbar",
        padding="1em",
        position="fixed",
        style={"background": "var(--accent-4)"},
        top="0px",
        width="100%",
        z_index="1000",
    )


def page(heading: Header, *children: str | rx.Component) -> rx.Component:
    """Return a page fragment with navbar and given children."""
    return rx.fragment(
        navbar(heading),
        rx.vstack(
            *children,
            justify="center",
            min_height="85vh",
            margin="4em 1em 1em",
            spacing="5",
        ),
    )
