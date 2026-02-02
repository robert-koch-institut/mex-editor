from collections.abc import Generator, Mapping
from importlib.metadata import version
from urllib.parse import parse_qs, urlencode, urlparse

import reflex as rx
from reflex.event import EventSpec

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.editor.label_var import label_var
from mex.editor.locale_service import LocaleService
from mex.editor.models import MergedLoginPerson, NavItem, User


class State(rx.State):
    """The base state for the app."""

    _locale_service = LocaleService.get()
    _available_locales = _locale_service.get_available_locales()

    current_locale: str = next(
        (x for x in _available_locales if x.id.lower().startswith("de")),
        _available_locales[0],
    ).id
    navigate_target: str | None = None
    user_mex: User | None = None
    user_ldap: User | None = None
    merged_login_person: MergedLoginPerson | None = None
    target_path_after_login: str | None = None
    _nav_items: list[NavItem] = [
        NavItem(
            title="layout.nav_bar.search_navitem",
            path="/",
            raw_path="/?page=1",
        ),
        NavItem(
            title="layout.nav_bar.create_navitem",
            path="/create",
            raw_path="/create/",
        ),
        NavItem(
            title="layout.nav_bar.edit_navitem",
            path="/item/[identifier]",
            raw_path=f"/item/{MEX_PRIMARY_SOURCE_STABLE_TARGET_ID}/",
        ),
        NavItem(
            title="layout.nav_bar.merge_navitem",
            path="/merge",
            raw_path="/merge/",
        ),
        NavItem(
            title="layout.nav_bar.ingest_navitem",
            path="/ingest",
            raw_path="/ingest/",
        ),
    ]

    def _translate_nav_item(self, item: NavItem) -> NavItem:
        return NavItem(
            title=self._locale_service.get_ui_label(self.current_locale, item.title),
            **item.dict(exclude={"title"}),
        )

    @rx.var
    def nav_items_translated(self) -> list[NavItem]:
        """The Navbar items with locale sensitive label."""
        return [self._translate_nav_item(item) for item in self._nav_items]

    @rx.event
    def change_locale(self, locale: str) -> None:
        """Change the current locale to the given one and reload the page.

        Args:
            locale: The locale to change to.
        """
        self.current_locale = locale

    @rx.event
    def logout(self) -> Generator[EventSpec]:
        """Log out a user."""
        self.reset()  # type: ignore[no-untyped-call]
        yield rx.redirect("/")

    @rx.event
    def check_mex_login(self) -> Generator[EventSpec]:
        """Check if a user is logged in."""
        if self.user_mex is None:
            self.target_path_after_login = str(self.router.url)
            yield rx.redirect("/login")

    @rx.event
    def check_ldap_login(self) -> Generator[EventSpec]:
        """Check if a user is logged in to ldap."""
        if self.user_ldap is None:
            self.target_path_after_login = str(self.router.url)
            yield rx.redirect("/login-ldap")

    @staticmethod
    def _update_raw_path(
        nav_item: NavItem,
        params: Mapping[str, int | str | list[str]],
    ) -> None:
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

    def push_url_params(
        self,
        params: Mapping[str, int | str | list[str]],
    ) -> EventSpec | None:
        """Event handler to push updated url parameter to the browser history."""
        for nav_item in self._nav_items:
            fullmatch = nav_item.path == "/"
            if (
                self.router.url.path == nav_item.path
                if fullmatch
                else self.router.url.path.startswith(nav_item.path)
            ):
                self._update_raw_path(nav_item, params)
                return rx.call_script(
                    f"window.history.pushState(null, '', '{nav_item.raw_path}');"
                )
        return None

    @rx.event
    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        for nav_item in self._nav_items:
            fullmatch = nav_item.path == "/"
            if (
                self.router.url.path == nav_item.path
                if fullmatch
                else self.router.url.path.startswith(nav_item.path)
            ):
                parsed_url = urlparse(self.router.url)
                params = parse_qs(parsed_url.query)
                self._update_raw_path(nav_item, params)
                nav_item.underline = "always"
            else:
                nav_item.underline = "none"

    @rx.var(cache=True)
    def editor_version(self) -> str:
        """Return the version of mex-editor."""
        return version("mex-editor")

    @rx.var(cache=True, initial_value="N/A")
    def backend_version(self) -> str:
        """Return the version of mex-backend."""
        connector = BackendApiConnector.get()
        # TODO(ND): use proper connector method when available (stop-gap MX-1984)
        response = connector.request("GET", "_system/check")
        return str(response.get("version", "N/A"))

    @label_var(label_id="components.titles.additional_titles")
    def label_additional_titles(self) -> None:
        """Label for titles.additional_titles."""

    @label_var(label_id="components.pagination.next_button")
    def label_pagination_next_button(self) -> None:
        """Label for pagination.next_button."""

    @label_var(label_id="components.pagination.previous_button")
    def label_pagination_previous_button(self) -> None:
        """Label for pagination.previous_button."""

    @label_var(label_id="layout.nav_bar.logout_button")
    def label_nav_bar_logout_button(self) -> None:
        """Label for nav_bar.logout_button."""
