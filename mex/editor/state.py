import reflex as rx
from reflex.event import EventSpec

from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID


class User(rx.Base):
    """Info on the currently logged-in user."""

    name: str
    authorization: str
    write_access: bool


class NavItem(rx.Base):
    """Model for one navigation bar item."""

    title: str
    href: str = "/"
    href_template: str
    underline: str = "none"


class State(rx.State):
    """The base state for the app."""

    user: User | None = None
    nav_items: list[NavItem] = [
        NavItem(title="Search", href_template=r"/"),
        NavItem(title="Edit", href_template=r"/item/{item_id}/"),
        NavItem(title="Merge", href_template=r"/merge/"),
    ]

    def logout(self, _) -> EventSpec:
        """Log out a user."""
        self.reset()
        return rx.redirect("/")

    def check_login(self) -> EventSpec | None:
        """Check if a user is logged in."""
        if self.user is None:
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
