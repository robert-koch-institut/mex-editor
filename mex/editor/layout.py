import reflex as rx

from mex.editor.state import NavItem, State


def user_button() -> rx.Component:
    """Return a user button with an icon that indicates their access rights."""
    return rx.button(
        rx.cond(
            State.user.write_access,  # type: ignore[union-attr]
            rx.icon(tag="user_round_cog"),
            rx.icon(tag="user_round"),
        ),
        variant="ghost",
        style={"marginTop": "0"},
    )


def user_menu() -> rx.Component:
    """Return a user menu with a trigger, the user's name and a logout button."""
    return rx.menu.root(
        rx.menu.trigger(user_button()),
        rx.menu.content(
            rx.menu.item(
                State.user.name,  # type: ignore[union-attr]
                disabled=True,
                style={"color": "var(--gray-12)"},
            ),
            rx.menu.separator(),
            rx.menu.item(
                "Logout",
                on_select=State.logout,
            ),
        ),
        custom_attrs={"data-testid": "user-menu"},
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        item.title,
        href=item.href,
        underline=item.underline,
        padding="0.2em",
    )


def mex_editor_logo() -> rx.Component:
    """Return the editor's logo with icon and label."""
    return rx.hstack(
        rx.icon(
            "file-pen-line",
            size=28,
        ),
        rx.heading(
            "MEx Editor",
            weight="medium",
            style={"userSelect": "none"},
        ),
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
    return rx.hstack(
        mex_editor_logo(),
        rx.divider(orientation="vertical", size="2"),
        rx.foreach(State.nav_items, nav_link),
        rx.divider(orientation="vertical", size="2"),
        user_menu(),
        rx.spacer(),
        rx.color_mode.button(),
        id="navbar",
        padding="1em",
        position="fixed",
        style={"background": "var(--accent-4)"},
        top="0px",
        width="100%",
        z_index="1000",
        custom_attrs={"data-testid": "nav-bar"},
    )


def page(*children: str | rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    return rx.cond(
        State.user,
        rx.fragment(
            nav_bar(),
            rx.hstack(
                *children,
                min_height="85vh",
                margin="2em 1em 1em",
                spacing="5",
            ),
            on_mount=State.load_page,
            on_unmount=State.unload_page,
        ),
        rx.center(
            rx.spinner(size="3"),
            style={"marginTop": "40vh"},
        ),
    )
