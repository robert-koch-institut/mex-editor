from collections.abc import Generator, Iterable
from typing import Literal

import reflex as rx
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

    results_extracted: rx.Field[list[SearchResult]] = rx.field(default_factory=list)
    results_merged: rx.Field[list[SearchResult]] = rx.field(default_factory=list)
    entity_types_merged: rx.Field[dict[str, bool]] = rx.field(
        default_factory=lambda: {k.stemType: False for k in MERGED_MODEL_CLASSES}
    )
    entity_types_extracted: rx.Field[dict[str, bool]] = rx.field(
        default_factory=lambda: {k.stemType: False for k in MERGED_MODEL_CLASSES}
    )
    limit: rx.Field[int] = rx.field(50)
    is_loading: rx.Field[bool] = rx.field(default=True)
    query_strings: rx.Field[dict[Literal["merged", "extracted"], str]] = rx.field(
        default_factory=lambda: {"merged": "", "extracted": ""}
    )
    results_count: rx.Field[dict[str, int]] = rx.field(
        default_factory=lambda: {"merged": 0, "extracted": 0}
    )
    total_count: rx.Field[dict[str, int]] = rx.field(
        default_factory=lambda: {"merged": 0, "extracted": 0}
    )
    selected_items: rx.Field[dict[str, int | None]] = rx.field(
        default_factory=lambda: {"merged": None, "extracted": None}
    )

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

    @rx.event(background=True)  # type: ignore[operator]
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
                had_primary_source=None,
                skip=0,
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
                stable_target_id=None,
                entity_type=entity_type,
                skip=0,
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
    def submit_merge_items(self) -> Generator[EventSpec | None, None, None]:
        """Submit merging of the items."""
        yield rx.toast.error(
            title="Not Implemented",
            description="Item merging is not yet implemented.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )
