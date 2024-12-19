import reflex as rx
from reflex.event import EventSpec

from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.editor.models import NavItem, User


class State(rx.State):
    """The base state for the app."""

    user: User | None = None
    target_path_after_login: str | None = None
    nav_items: list[NavItem] = [
        NavItem(title="Search", href_template=r"/"),
        NavItem(title="Edit", href_template=r"/item/{item_id}/"),
        NavItem(title="Merge", href_template=r"/merge/"),
    ]

    def logout(self) -> EventSpec:
        """Log out a user."""
        self.reset()
        return rx.redirect("/")

    def check_login(self) -> EventSpec | None:
        """Check if a user is logged in."""
        if self.user is None:
            self.target_path_after_login = self.router.page.raw_path
            return rx.redirect("/login")
        return None

    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        self.item_id = self.router.page.params.get("item_id")
        item_id = self.item_id or MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
        for nav_item in self.nav_items:
            nav_item.href = nav_item.href_template.format(item_id=item_id)
            current_nav = self.router.page.raw_path == nav_item.href
            nav_item.underline = "always" if current_nav else "none"
