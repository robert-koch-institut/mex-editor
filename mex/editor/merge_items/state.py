from typing import Annotated

import reflex as rx
from pydantic import Field

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import MERGED_MODEL_CLASSES
from mex.editor.search.models import SearchPrimarySource, SearchResult
from mex.editor.state import State


class MergeState(State):
    """State management for the search page."""

    results_extracted: list[SearchResult] = []
    results_merged: list[SearchResult] = []
    total: Annotated[int, Field(ge=0)] = 0
    query_string: Annotated[str, Field(max_length=1000)] = ""
    entity_types: dict[str, bool] = {k.stemType: False for k in MERGED_MODEL_CLASSES}
    had_primary_sources: dict[str, SearchPrimarySource] = {}
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    is_loading: bool = False

    @rx.var(cache=False)
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

    @rx.event
    def set_entity_type(
        self,
        index: str,
        value: bool,  # noqa: FBT001
    ) -> None:
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value

    @rx.event
    def refresh(self) -> None:
        """Refresh the search results."""
        BackendApiConnector.get()

    @rx.event
    def submit_merge_items(self) -> None:
        """Submit merging of the items."""
        BackendApiConnector.get()
