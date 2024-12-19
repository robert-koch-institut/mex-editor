import math
from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.logging import logger
from mex.common.models import MERGED_MODEL_CLASSES_BY_NAME
from mex.common.wikidata.connector import WikidataQueryServiceConnector
from mex.editor.models import FixedValue
from mex.editor.state import State


class AuxResult(rx.Base):
    """Search result preview."""

    identifier: str
    title: list[FixedValue]
    preview: list[FixedValue]


class AuxState(State):
    """State management for the aux extractor search page."""

    results: list[AuxResult] = []
    total: int = 0
    query_string: str = ""
    entity_types: dict[str, bool] = {k: False for k in MERGED_MODEL_CLASSES_BY_NAME}
    current_page: int = 1
    limit: int = 50
    aux_items: list[str] = ["Wikidata", "LDAP"]

    @rx.var
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i+1}" for i in range(math.ceil(self.total / self.limit))]

    @rx.var
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

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

    def search(self) -> Generator[EventSpec | None, None, None]:
        """Search for wikidata items based on the query string."""
        connector = WikidataQueryServiceConnector.get()
        try:
            response = connector.get_data_by_query(self.query_string)
        except HTTPError as exc:
            self.reset()
            logger.error(
                "backend error fetching wikidata items: %s",
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
            self.total = len(response)

    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search page."""
        self.reset()
        return self.search()
