import contextlib
import math
from collections.abc import Generator
from urllib.parse import urlencode

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import MERGED_MODEL_CLASSES_BY_NAME
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State


class SearchState(State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: int = 0
    query_string: str = ""
    entity_types: dict[str, bool] = {k: False for k in MERGED_MODEL_CLASSES_BY_NAME}
    current_page: int = 1
    limit: int = 50

    def _load_url_params(self) -> None:
        """Load url params into the state."""
        print("loading url params", self.router.page.params)
        with contextlib.suppress(ValueError):
            self.current_page = int(self.router.page.params.get("page", ""))
        self.query_string = self.router.page.params.get("q", "")
        selected_types = self.router.page.params.get("entityType", "")
        self.entity_types = {
            k: k in selected_types for k in MERGED_MODEL_CLASSES_BY_NAME
        }

    def _push_url_params(self) -> Generator[EventSpec | None, None, None]:
        """Update the url with variables from the state."""
        url_params = urlencode(
            [
                (key, value)
                for key, value in (
                    [("q", self.query_string)] if self.query_string else []
                )
                + ([("page", self.current_page)] if self.current_page > 1 else [])
                + [("entityType", k) for k, v in self.entity_types.items() if v]
                if value
            ]
        )
        for nav_item in self.nav_items:
            if nav_item.title == "Search":
                nav_item.href = f"/?{url_params}"
                nav_item.href_template = f"/?{url_params}"
        new_path = f"{self.router.page.path}?{url_params}"
        print("pushing url params", new_path)
        yield rx.call_script(f"window.history.pushState(null, '', '{new_path}');")

    @rx.var(cache=False)
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var(cache=False)
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        max_page = math.ceil(self.total / self.limit)
        return self.current_page >= max_page

    @rx.var(cache=False)
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

    @rx.var(cache=False)
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / self.limit))]

    @rx.event
    def set_query_string(self, value: str) -> Generator[EventSpec | None, None, None]:
        """Set the query string and refresh the results."""
        self.query_string = value
        self.current_page = 1
        yield from self._push_url_params()
        yield from self.search()

    @rx.event
    def set_entity_type(
        self, index: str, value: bool
    ) -> Generator[EventSpec | None, None, None]:
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value
        self.current_page = 1
        yield from self._push_url_params()
        yield from self.search()

    @rx.event
    def set_page(
        self, page_number: str | int
    ) -> Generator[EventSpec | None, None, None]:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
        yield from self._push_url_params()
        yield from self.search()

    @rx.event
    def go_to_previous_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the previous page."""
        yield from self.set_page(self.current_page - 1)

    @rx.event
    def go_to_next_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the next page."""
        yield from self.set_page(self.current_page + 1)

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results."""
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_string,
                entity_type=[k for k, v in self.entity_types.items() if v],
                skip=self.limit * (self.current_page - 1),
                limit=self.limit,
            )
        except HTTPError as exc:
            self.results = []
            self.total = 0
            self.current_page = 1
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.results = transform_models_to_results(response.items)
            self.total = response.total
            yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search page."""
        self._load_url_params()
        yield from self.search()
