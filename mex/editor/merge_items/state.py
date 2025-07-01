from collections.abc import Generator
from typing import Annotated, Literal

import reflex as rx
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import MERGED_MODEL_CLASSES
from mex.common.transform import ensure_prefix
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State


class MergeState(State):
    """State management for the merge items page."""

    results_extracted: list[SearchResult] = []
    results_merged: list[SearchResult] = []
    total_merged: Annotated[int, Field(ge=0)] = 0
    total_extracted: Annotated[int, Field(ge=0)] = 0
    query_string_merged: Annotated[str, Field(max_length=1000)] = ""
    query_string_extracted: Annotated[str, Field(max_length=1000)] = ""
    entity_types_merged: dict[str, bool] = {
        k.stemType: False for k in MERGED_MODEL_CLASSES
    }
    entity_types_extracted: dict[str, bool] = {
        k.stemType: False for k in MERGED_MODEL_CLASSES
    }
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    is_loading: bool = False
    selected_merged_index: int | None = None
    selected_extracted_index: int | None = None

    @rx.event
    def select_item(self, category: Literal["merged", "extracted"], index: int) -> None:
        """Select or deselect a merged or extracted item based on the index."""
        if category == "merged":
            if self.selected_merged_index == index:
                self.selected_merged_index = None
                return
            self.selected_merged_index = index
        elif category == "extracted":
            if self.selected_extracted_index == index:
                self.selected_extracted_index = None
                return
            self.selected_extracted_index = index

    @rx.var
    def results_merged_count(self) -> int:
        """Return the count of merged results."""
        return len(self.results_merged)

    @rx.var
    def results_extracted_count(self) -> int:
        """Return the count of extracted results."""
        return len(self.results_extracted)

    @rx.event
    def handle_submit_extracted(self, form_data: str) -> None:
        """Handle the extracted form submit."""
        self.query_string_extracted = form_data

    @rx.event
    def handle_submit_merged(self, form_data: str) -> None:
        """Handle the merged form submit."""
        self.query_string_merged = form_data

    @rx.event
    def set_entity_type_merged(
        self,
        index: str,
        value: bool,  # noqa: FBT001
    ) -> None:
        """Set the entity type for filtering and refresh the merged results."""
        self.entity_types_merged[index] = value

    @rx.event
    def set_entity_type_extracted(
        self,
        index: str,
        value: bool,  # noqa: FBT001
    ) -> None:
        """Set the entity type for filtering and refresh the extracted results."""
        self.entity_types_extracted[index] = value

    @rx.event
    def clear_input_merged(self) -> None:
        """Clear the merged search input and reset the results."""
        self.query_string_merged = ""
        self.entity_types_merged = dict.fromkeys(self.entity_types_merged, False)
        self.results_merged = []
        self.selected_merged_index = None
        self.total_merged = 0

    @rx.event
    def clear_input_extracted(self) -> None:
        """Clear the extracted search input and reset the results."""
        self.query_string_extracted = ""
        self.entity_types_extracted = dict.fromkeys(self.entity_types_extracted, False)
        self.results_extracted = []
        self.selected_extracted_index = None
        self.total_extracted = 0

    @rx.event
    def refresh_merged(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results for merged items."""
        connector = BackendApiConnector.get()
        self.selected_merged_index = None
        entity_type = [
            ensure_prefix(k, "Merged") for k, v in self.entity_types_merged.items() if v
        ]
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_string_merged,
                entity_type=entity_type,
                had_primary_source=None,
                skip=0,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_merged = []
            self.total = 0
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results_merged = transform_models_to_results(response.items)
            self.total_merged = response.total

    @rx.event
    def refresh_extracted(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results for extracted items."""
        connector = BackendApiConnector.get()
        self.selected_extracted_index = None
        entity_type = [
            ensure_prefix(k, "Extracted")
            for k, v in self.entity_types_extracted.items()
            if v
        ]
        self.results_extracted = self.results_extracted
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_extracted_items(
                query_string=self.query_string_extracted,
                stable_target_id=None,
                entity_type=entity_type,
                skip=0,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_extracted = []
            self.total = 0
            yield None
            yield from escalate_error(
                "backend", "error fetching extracted items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results_extracted = transform_models_to_results(response.items)
            self.total_extracted = response.total

    @rx.event
    def submit_merge_items(self) -> None:
        """Submit merging of the items."""
        BackendApiConnector.get()

    @rx.event
    def refresh(self) -> None:
        """Reset the state."""
        self.reset()
