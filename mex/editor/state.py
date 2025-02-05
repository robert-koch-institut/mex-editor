from urllib.parse import urlencode

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
            raw_path="/?page=1",
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

    @staticmethod
    def _update_raw_path(nav_item: NavItem, **params: int | str | list[str]) -> None:
        """Update the raw path of a nav item with the given parameters."""
        raw_path = nav_item.path
        param_tuples = list(params.items())
        for key, value in param_tuples:
            if f"[{key}]" in raw_path:
                raw_path = raw_path.replace(f"[{key}]", f"{value}")
        query_tuples: list[tuple[str, str]] = []
        for key, value in param_tuples:
            if f"[{key}]" not in nav_item.path:
                value_list = value if isinstance(value, list) else [f"{value}"]
                query_tuples.extend((key, item) for item in value_list if item)
        if query_str := urlencode(query_tuples):
            raw_path = f"{raw_path}?{query_str}"
        nav_item.raw_path = raw_path

    @rx.event
    def push_url_params(self, **params: int | str | list[str]) -> EventSpec | None:
        """Event handler to push updated url parameter to the browser history."""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                self._update_raw_path(nav_item, **params)
                return rx.call_script(
                    f"window.history.pushState(null, '', '{nav_item.raw_path}');"
                )
        return None

    @rx.event
    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                self._update_raw_path(nav_item, **self.router.page.params)
                nav_item.underline = "always"
            else:
                nav_item.underline = "none"
