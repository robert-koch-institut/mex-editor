import math
from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.backend_api.models import ExtractedItemsResponse
from mex.common.logging import logger
from mex.editor.aux_search.models import AuxResult
from mex.editor.aux_search.transform import transform_models_to_results
from mex.editor.state import State


class AuxState(State):
    """State management for the aux extractor search page."""

    results: list[AuxResult] = []
    total: int = 0
    query_string: str = ""
    current_page: int = 1
    limit: int = 10
    aux_data_sources: list[str] = ["Wikidata", "LDAP"]

    @rx.var
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i+1}" for i in range(math.ceil(self.total / self.limit))]

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

    def toggle_show_properties(self, result: AuxResult) -> None:
        """Toggle the show properties state."""
        result.show_properties = False

    def set_query_string(self, value: str) -> Generator[EventSpec | None, None, None]:
        """Set the query string and refresh the results."""
        self.query_string = value
        return self.search()

    def set_page(
        self, page_number: str | int
    ) -> Generator[EventSpec | None, None, None]:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
        return self.search()

    def go_to_previous_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the previous page."""
        return self.set_page(self.current_page - 1)

    def go_to_next_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the next page."""
        return self.set_page(self.current_page + 1)

    def search(self) -> Generator[EventSpec | None, None, None]:
        """Search for wikidata organizations based on the query string."""
        if self.query_string == "":
            return
        connector = BackendApiConnector.get()
        try:
            response = connector.request(
                method="GET",
                endpoint="wikidata",
                params={
                    "q": self.query_string,
                    "offset": str((self.current_page - 1) * self.limit),
                    "limit": str(self.limit),
                },
            )
        except HTTPError as exc:
            self.reset()
            logger.error(
                "error fetching wikidata items: %s",
                exc.response.text,
                exc_info=False,
            )
            yield rx.toast.error(
                exc.response.text,
                duration=5000,
                close_button=True,
                dismissible=True,
            )
        else:
            yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            response = ExtractedItemsResponse.model_validate(response)  # type: ignore[assignment]
            self.results = transform_models_to_results(response.items)  # type: ignore[arg-type]
            self.total = response.total  # type: ignore[attr-defined]

    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search page."""
        self.reset()
        return self.search()
