import reflex as rx
from reflex.event import EventSpec

from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.editor.models import NavItem, User


class State(rx.State):
    """The base state for the app."""

    user: User | None = None
    target_path_after_login: str | None = None
    nav_items: list[NavItem] = [
        NavItem(
            title="Search",
            path="/",
            raw_path="/",
        ),
        NavItem(
            title="Edit",
            path="/item/[identifier]",
            raw_path=f"/item/{MEX_PRIMARY_SOURCE_STABLE_TARGET_ID}/",
        ),
        NavItem(
            title="Merge",
            path="/merge",
            raw_path="/merge/",
        ),
        NavItem(
            title="Aux Import",
            path="/aux-import",
            raw_path="/aux-import/",
        ),
    ]

    @rx.event
    def logout(self) -> EventSpec:
        """Log out a user."""
        self.reset()
        return rx.redirect("/")

    @rx.event
    def check_login(self) -> EventSpec | None:
        """Check if a user is logged in."""
        if self.user is None:
            self.target_path_after_login = self.router.page.raw_path
            return rx.redirect("/login")
        return None

    @rx.event
    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                nav_item.update_raw_path(self.router.page.params)
                nav_item.underline = "always"
            else:
                nav_item.underline = "none"
