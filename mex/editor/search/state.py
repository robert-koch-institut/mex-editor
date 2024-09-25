import math

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import MERGED_MODEL_CLASSES_BY_NAME
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results


class SearchState(rx.State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: int = 0
    query_string: str = ""
    entity_types: dict[str, bool] = {k: False for k in MERGED_MODEL_CLASSES_BY_NAME}
    current_page: int = 1
    limit: int = 10

    @rx.var
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        max_page = math.ceil(self.total / self.limit)
        return self.current_page >= max_page

    @rx.var
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

    @rx.var
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i+1}" for i in range(math.ceil(self.total / self.limit))]

    def set_query_string(self, value: str) -> EventSpec | None:
        """Set the query string and refresh the results."""
        self.query_string = value
        return self.refresh()

    def set_entity_type(self, value, index) -> EventSpec | None:
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value
        return self.refresh()

    def set_page(self, page_number: str | int) -> EventSpec | None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
        return self.refresh()

    def go_to_previous_page(self) -> EventSpec | None:
        """Navigate to the previous page."""
        return self.set_page(self.current_page - 1)

    def go_to_next_page(self) -> EventSpec | None:
        """Navigate to the next page."""
        return self.set_page(self.current_page + 1)

    def refresh(self) -> EventSpec | None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_merged_items(
                self.query_string,
                [k for k, v in self.entity_types.items() if v],
                self.limit * (self.current_page - 1),
                self.limit,
            )
        except HTTPError as exc:
            self.reset()
            logger.error("backend error: %s", exc.response.text, exc_info=False)
            return rx.toast.error(
                exc.response.text,
                duration=5000,
                close_button=True,
                dismissible=True,
            )
        self.results = transform_models_to_results(response.items)
        self.total = response.total
        return None
