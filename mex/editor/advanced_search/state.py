from typing import Any

import reflex as rx

from mex.common.fields import REFERENCE_FIELDS_BY_CLASS_NAME
from mex.common.models import MERGED_MODEL_CLASSES
from mex.common.transform import ensure_prefix
from mex.editor.fields import STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME
from mex.editor.label_var import label_var
from mex.editor.state import State
from mex.editor.value_label_select import ValueLabelSelectItem


class RefFilter(rx.Base):
    field: str = ""
    field_label: str = ""
    reference_value_type: list[str] = []
    values: list[str] = []


class AdvancedSearchState(State):
    query: str = ""
    entity_types: list[str] = []
    refs: list[RefFilter] = []

    all_entity_types = [k.stemType for k in MERGED_MODEL_CLASSES]

    @rx.var
    def all_fields_for_entity_types(self) -> list[ValueLabelSelectItem]:
        """Get all fields for the currently selected entity types filter.

        Returns:
            The fields for the selected entity types.
        """
        selected_entity_types = (
            self.all_entity_types if len(self.entity_types) == 0 else self.entity_types
        )

        fields_with_type = [
            [
                ValueLabelSelectItem(
                    value=f"{entity_type}.{field}",
                    label=self._locale_service.get_field_label(
                        self.current_locale, entity_type, field
                    ),
                )
                for field in REFERENCE_FIELDS_BY_CLASS_NAME[
                    ensure_prefix(entity_type, "Extracted")
                ]
            ]
            for entity_type in selected_entity_types
        ]

        return sorted(
            {
                item.value: item
                for item in [f for fields in fields_with_type for f in fields]
            }.values(),
            key=lambda x: x.label,
        )

    def _get_field_data(self, field: str) -> dict:
        found_field = next(
            (x for x in self.all_fields_for_entity_types if x.value == field), None
        )

        [entity_type, field_name] = field.split(".")
        entity_type = ensure_prefix(entity_type, "Extracted")
        return {
            "field_label": found_field.label if found_field else field,
            "reference_value_type": STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME[
                entity_type
            ].get(field_name, [])
            if entity_type in STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME
            else [],
        }

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
        print(
            "REMOVING", self.refs[index].values[val_index], val_index, self.refs[index]
        )
        self.refs[index].values.pop(val_index)
        print("REMOVED", self.refs[index].values)

    @label_var(label_id="search.search_input.placeholder")
    def label_search_input_placeholder(self) -> None:
        """Label for search_input.placeholder."""

    @label_var(label_id="search.reference_field_filter.placeholder")
    def label_reference_field_filter_placeholder(self) -> None:
        """Label for reference_field_filter.placeholder."""
