from collections.abc import Generator
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
    def _update_raw_path(nav_item: NavItem, **params: int | str | list[str]) -> str:
        """Render the parameters into a raw path."""
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
        return query_str

    @rx.event
    def push_url_params(
        self, **params: int | str | list[str]
    ) -> Generator[EventSpec | None, None, None]:
        """Return the current nav item."""
        url_params = ""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                url_params = self._update_raw_path(nav_item, **params)
        new_path = f"{self.router.page.path}?{url_params}".rstrip("?")
        yield rx.call_script(f"window.history.pushState(null, '', '{new_path}');")

    @rx.event
    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                self._update_raw_path(nav_item, **self.router.page.params)
                nav_item.underline = "always"
            else:
                nav_item.underline = "none"
