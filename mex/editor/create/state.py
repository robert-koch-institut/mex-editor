import reflex as rx

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models.resource import (
    AdditiveResource,
    PreventiveResource,
    SubtractiveResource,
)
from mex.editor.create.transform import transform_model_to_template_fields
from mex.editor.edit.models import EditorField, EditorPrimarySource
from mex.editor.models import EditorValue
from mex.editor.state import State


class CreateState(State):
    """State for the edit component."""

    fields: list[EditorField] = []
    entity_type: str = "ExtractedResource"

    @rx.event
    def change_entity_type(self, entity_type: str):
        """Change the select value var."""
        self.entity_type = entity_type
        self.refresh()

    @rx.event
    def refresh(self) -> None:
        """Refresh the edit page."""
        self.reset()
        if self.entity_type:
            self.fields = transform_model_to_template_fields(
                self.entity_type,
                additive=AdditiveResource(),
                subtractive=PreventiveResource(),  # type: ignore[arg-type]
                preventive=SubtractiveResource(),  # type: ignore[arg-type]
            )
        for field in self.fields:
            for source in field.primary_sources:
                if not source.editor_values:
                    source.editor_values.append(EditorValue())

    @rx.event
    def submit_new_item(self) -> None:
        """Convert the fields to a rule set and submit it to the backend."""
        BackendApiConnector.get()

    def _get_primary_sources_by_field_name(
        self, field_name: str
    ) -> list[EditorPrimarySource]:
        """Get all primary sources for the given field name."""
        for field in self.fields:
            if field.name == field_name:
                return field.primary_sources
        msg = f"field not found: {field_name}"
        raise ValueError(msg)

    def _get_editable_primary_source_by_field_name(
        self, field_name: str
    ) -> EditorPrimarySource:
        """Get the (first) primary source that allows an editable rule."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.input_config.allow_additive:
                return primary_source
        msg = f"editable field not found: {field_name}"
        raise ValueError(msg)

    @rx.event
    def set_text_value(self, field_name: str, index: int, value: str) -> None:
        """Set the text attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].text = value

    @rx.event
    def set_badge_value(self, field_name: str, index: int, value: str) -> None:
        """Set the badge attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].badge = value

    @rx.event
    def set_href_value(self, field_name: str, index: int, value: str) -> None:
        """Set an external href on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].href = value
        primary_source.editor_values[index].external = True
