from collections.abc import Generator, Iterable
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
from mex.editor.utils import resolve_editor_value


class MergeState(State):
    """State management for the merge items page."""

    results_extracted: list[SearchResult] = []
    results_merged: list[SearchResult] = []
    entity_types_merged: dict[str, bool] = {
        k.stemType: False for k in MERGED_MODEL_CLASSES
    }
    entity_types_extracted: dict[str, bool] = {
        k.stemType: False for k in MERGED_MODEL_CLASSES
    }
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    is_loading: bool = True
    query_strings: dict[Literal["merged", "extracted"], str] = {
        "merged": "",
        "extracted": "",
    }
    results_count: dict[str, int] = {
        "merged": 0,
        "extracted": 0,
    }
    total_count: dict[str, int] = {
        "merged": 0,
        "extracted": 0,
    }
    selected_items: dict[str, int | None] = {
        "merged": None,
        "extracted": None,
    }

    @rx.event
    def select_item(self, category: Literal["merged", "extracted"], index: int) -> None:
        """Select or deselect a merged or extracted item based on the index."""
        if self.selected_items[category] == index:
            self.selected_items[category] = None
            return
        self.selected_items[category] = index

    @rx.event
    def handle_submit(
        self, category: Literal["merged", "extracted"], form_data: str
    ) -> None:
        """Handle the extracted or merged form submit."""
        self.query_strings[category] = form_data

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
    def clear_input(self, category: Literal["merged", "extracted"]) -> None:
        """Clear the merged or extracted search input and reset the results."""
        self.query_strings[category] = ""
        self.selected_items[category] = None
        self.results_count[category] = 0
        self.total_count[category] = 0
        if category == "merged":
            self.entity_types_merged = dict.fromkeys(self.entity_types_merged, False)
            self.results_merged = []
        else:
            self.entity_types_extracted = dict.fromkeys(
                self.entity_types_extracted, False
            )
            self.results_extracted = []

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result_list in (self.results_merged, self.results_extracted):
            for result in result_list:
                for preview in result.preview:
                    if preview.identifier and not preview.text:
                        async with self:
                            await resolve_editor_value(preview)

    @rx.event
    def refresh(
        self,
        categories: Iterable[Literal["merged", "extracted"]] = ("merged", "extracted"),
    ) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results for the specified category."""
        if "merged" in categories:
            self.selected_items["merged"] = None
            yield from self._refresh_merged()
        if "extracted" in categories:
            self.selected_items["extracted"] = None
            yield from self._refresh_extracted()

    def _refresh_merged(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results for merged items."""
        connector = BackendApiConnector.get()
        entity_type = [
            ensure_prefix(k, "Merged") for k, v in self.entity_types_merged.items() if v
        ]
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_strings["merged"],
                entity_type=entity_type,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_merged = []
            self.results_count["merged"] = 0
            self.total_count["merged"] = 0
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results_merged = transform_models_to_results(response.items)
            self.results_count["merged"] = len(self.results_merged)
            self.total_count["merged"] = response.total

    def _refresh_extracted(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results for extracted items."""
        connector = BackendApiConnector.get()
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
                query_string=self.query_strings["extracted"],
                entity_type=entity_type,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_extracted = []
            self.results_count["extracted"] = 0
            self.total_count["extracted"] = 0
            yield None
            yield from escalate_error(
                "backend", "error fetching extracted items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results_extracted = transform_models_to_results(response.items)
            self.results_count["extracted"] = len(self.results_extracted)
            self.total_count["extracted"] = response.total

    @rx.event
    def submit_merge_items(self) -> Generator[EventSpec, None, None]:
        """Submit merging of the items."""
        yield rx.toast.error(
            title="Not Implemented",
            description="Item merging is not yet implemented.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )
