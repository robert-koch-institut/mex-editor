import math

import reflex as rx
from pydantic import BaseModel
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import (
    MERGED_MODEL_CLASSES_BY_NAME,
    AnyMergedModel,
)
from mex.editor.search.models import SearchResult
from mex.editor.transform import render_model_preview, render_model_title


class _BackendSearchResponse(BaseModel):
    total: int
    items: list[AnyMergedModel]


class SearchState(rx.State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: int = 0
    query_string: str = ""
    entity_types: dict[str, bool] = {k: False for k in MERGED_MODEL_CLASSES_BY_NAME}

    current_page: int = 1
    limit: int = 50

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

    def set_query_string(self, value: str):
        """Set the query string and refresh the results."""
        self.query_string = value
        self.refresh()

    def set_entity_type(self, value, index):
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value
        self.refresh()

    def set_page(self, page_number: str | int):
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
        self.refresh()

    def go_to_previous_page(self):
        """Navigate to the previous page."""
        self.set_page(self.current_page - 1)

    def go_to_next_page(self):
        """Navigate to the next page."""
        self.set_page(self.current_page + 1)

    def refresh(self) -> None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()

        # TODO: use a specialized merged-item search method (stop-gap MX-1581)
        try:
            response = connector.request(
                "GET",
                "merged-item",
                params={
                    "q": self.query_string,
                    "entityType": [k for k, v in self.entity_types.items() if v],  # type: ignore
                    "skip": str(self.limit * (self.current_page - 1)),
                    "limit": str(self.limit),
                },
            )
        except HTTPError as exc:
            self.results = []
            self.total = 0
            logger.error("backend error: ", exc.response.text)
            return
        items = _BackendSearchResponse.model_validate(response).items
        self.results = [
            SearchResult(
                identifier=item.identifier,
                title=render_model_title(item),
                preview=render_model_preview(item),
            )
            for item in items
        ]
        self.total = response["total"]
