import math

import reflex as rx

from mex.common.models import MERGED_MODEL_CLASSES_BY_NAME
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

    def set_query_string(self, value: str) -> None:
        """Set the query string and refresh the results."""
        self.query_string = value

    def set_page(self, page_number: str | int) -> None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
