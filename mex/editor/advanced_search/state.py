from collections.abc import Generator, Iterable
from itertools import groupby
from typing import Any

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.fields import REFERENCE_FIELDS_BY_CLASS_NAME
from mex.common.models import MERGED_MODEL_CLASSES
from mex.common.transform import ensure_prefix
from mex.editor.exceptions import escalate_error
from mex.editor.fields import STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME
from mex.editor.label_var import label_var
from mex.editor.models import SearchResult
from mex.editor.pagination_component import PaginationStateMixin
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value
from mex.editor.value_label_select import ValueLabelSelectItem


class RefFilter(rx.Base):
    """Model to filter reference fields by values."""

    field: str = ""
    field_label: str = ""
    reference_value_type: list[str] = []
    values: list[str] = []


class AdvancedSearchState(State, PaginationStateMixin):
    """State for the advanced search page."""

    query: str = ""
    entity_types: list[str] = []
    refs: list[RefFilter] = []

    all_entity_types = [k.stemType for k in MERGED_MODEL_CLASSES]

    is_searching: bool = False
    search_results: list[SearchResult] = []

    @rx.var
    def all_fields_for_entity_types(self) -> list[ValueLabelSelectItem]:
        """Get all fields for the currently selected entity types filter.

        Returns:
            The fields for the selected entity types.
        """
        selected_entity_types = (
            self.all_entity_types if len(self.entity_types) == 0 else self.entity_types
        )

        fields_with_type: list[dict] = [
            {
                "field": field,
                "label": self._locale_service.get_field_label(
                    self.current_locale, entity_type, field
                ),
                "value_types": STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME[
                    ensure_prefix(entity_type, "Extracted")
                ][field],
            }
            for entity_type in selected_entity_types
            for field in REFERENCE_FIELDS_BY_CLASS_NAME[
                ensure_prefix(entity_type, "Extracted")
            ]
        ]

        fields_with_all_ref_types_and_label: dict[str, set[str]] = {}
        for k, g in groupby(fields_with_type, lambda x: x["field"]):
            group = list(g)
            field_key = f"{k}::{group[0]['label']}"

            for item in group:
                if field_key not in fields_with_all_ref_types_and_label:
                    fields_with_all_ref_types_and_label[field_key] = set()
                fields_with_all_ref_types_and_label[field_key].update(
                    item["value_types"]
                )

        def _build_select_item(key: str, value: Iterable[str]) -> ValueLabelSelectItem:
            [field, label] = key.split("::")
            return ValueLabelSelectItem(label=label, value=f"{field}:{','.join(value)}")

        return sorted(
            [
                _build_select_item(key, value)
                for key, value in fields_with_all_ref_types_and_label.items()
            ],
            key=lambda x: x.label,
        )

    @rx.var
    def search_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.search_results)

    def _get_field_data(self, field_value: str) -> dict:
        found_field = next(
            (x for x in self.all_fields_for_entity_types if x.value == field_value),
            None,
        )
        [field_name, value_types_str] = field_value.split(":")
        value_types = value_types_str.split(",")
        return {
            "field_label": found_field.label if found_field else field_value,
            "reference_value_type": value_types,
            "field_name": field_name,
        }

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        """Perform the search with the current filters."""
        entity_type = [ensure_prefix(x, "Merged") for x in self.entity_types]

        skip = self.limit * (self.current_page - 1)

        # TODO(FE): rework when updated fetch method is here
        ref = self.refs[0] if self.refs else None
        ref_field = (
            self._get_field_data(ref.field)["field_name"]
            if ref and ref.values
            else None
        )
        ref_values = ref.values if ref and ref.values else None

        self.is_searching = True
        yield None

        connector = BackendApiConnector.get()
        try:
            fetch_result = connector.fetch_preview_items(
                query_string=self.query if self.query else None,
                entity_type=entity_type,
                referenced_identifier=ref_values,
                reference_field=ref_field,
                skip=skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.search_results = []
            self.total = 0
            self.current_page = 1
            yield from escalate_error(
                "backend",
                "advanced search :: error fetching preview items",
                exc.response.text,
            )
        else:
            self.search_results = transform_models_to_results(fetch_result.items)
            self.total = fetch_result.total

        self.is_searching = False

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.search_results:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)

    @rx.event
    def on_query_form_submit(self, form_data: dict[str, Any]) -> None:
        """Handle the submission of the query form."""
        self.query = form_data.get("query", self.query)

    @rx.event
    def toggle_entity_type(self, entity_type: str) -> None:
        """Toggle the selection of an entity type."""
        if entity_type in self.entity_types:
            self.entity_types.remove(entity_type)
        else:
            self.entity_types.append(entity_type)

    @rx.event
    def add_ref_filter(self, field: str) -> None:
        """Add a reference filter.

        Args:
            field: The field to filter on.
            values: The values to filter by.
        """
        field_data = self._get_field_data(field)
        self.refs.append(RefFilter(field=field, values=[], **field_data))

    @rx.event
    def remove_ref_filter(self, index: int) -> None:
        """Remove a reference filter.

        Args:
            index: The index of ref filter to remove.
        """
        self.refs.pop(index)

    @rx.event
    def set_ref_filter_field(self, index: int, field: str) -> None:
        """Set the field for a reference filter.

        Args:
            index: The index of the reference filter to update.
            field: The new field.
        """
        ref = self.refs[index]
        field_data = self._get_field_data(field)

        ref.field = field
        ref.field_label = field_data["field_label"]
        ref.reference_value_type = field_data["reference_value_type"]

    @rx.event
    def add_ref_filter_value(self, index: int, value: str) -> None:
        """Add a value to a reference filter.

        Args:
            index: The index of the reference filter to update.
            value: The value to add.
        """
        self.refs[index].values.append(value)

    @rx.event
    def set_ref_filter_value(self, index: int, val_index: int, value: str) -> None:
        """Set a value for a reference filter.

        Args:
            index: The index of the reference filter to update.
            val_index: The index of the value to update.
            value: The new value.
        """
        self.refs[index].values[val_index] = value

    @rx.event
    def remove_ref_filter_value(self, index: int, val_index: int) -> None:
        """Remove a value from a reference filter.

        Args:
            index: The index of the reference filter to update.
            val_index: The index of the value to remove.
        """
        self.refs[index].values.pop(val_index)

    @label_var(label_id="search.search_input.placeholder")
    def label_search_input_placeholder(self) -> None:
        """Label for search_input.placeholder."""

    @label_var(label_id="search.reference_field_filter.placeholder")
    def label_reference_field_filter_placeholder(self) -> None:
        """Label for reference_field_filter.placeholder."""

    @label_var(
        label_id="search.result_summary.format",
        deps=["search_results_length", "total"],
    )
    def label_result_summary_format(self) -> list[int]:
        """Label for result_summary.format."""
        return [self.search_results_length, self.total]

    @label_var(label_id="advanced_search.reference_filter.add_value")
    def label_reference_filter_add_value(self) -> None:
        """Label for reference_filter.add_value."""

    @label_var(label_id="advanced_search.reference_filter.remove_value")
    def label_reference_filter_remove_value(self) -> None:
        """Label for reference_filter.remove_value."""

    @label_var(label_id="advanced_search.reference_filter.value_placeholder")
    def label_reference_filter_value_placeholder(self) -> None:
        """Label for reference_filter.value_placeholder."""

    @label_var(label_id="advanced_search.reference_filter.title")
    def label_refrence_filter_title(self) -> None:
        """Label for refrence_filter.title."""
