from collections.abc import Generator

import reflex as rx
from pydantic import ValidationError
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models.resource import (
    AdditiveResource,
    PreventiveResource,
    SubtractiveResource,
)
from mex.common.transform import ensure_prefix
from mex.editor.create.transform import transform_model_to_template_fields
from mex.editor.edit.models import EditorField, EditorPrimarySource, ValidationMessage
from mex.editor.edit.transform import (
    transform_fields_to_rule_set,
    transform_validation_error_to_messages,
)
from mex.editor.exceptions import escalate_error
from mex.editor.models import EditorValue
from mex.editor.state import State
from mex.editor.utils import resolve_identifier


class CreateState(State):
    """State for the edit component."""

    fields: list[EditorField] = []
    entity_type: str = "Resource"
    validation_messages: list[ValidationMessage] = []

    @rx.event
    def refresh(self) -> None:
        """Refresh the edit page."""
        self.fields.clear()
        self.validation_messages.clear()
        if self.entity_type:
            self.fields = transform_model_to_template_fields(
                ensure_prefix(self.entity_type, "Extracted"),
                additive=AdditiveResource(),
                subtractive=SubtractiveResource(),
                preventive=PreventiveResource(),
            )

    @rx.event
    def clean_up_editor_values(self) -> None:
        """Remove empty editor values."""
        for field in self.fields:
            for primary_source in field.primary_sources:
                primary_source.editor_values = [
                    value
                    for value in primary_source.editor_values
                    if not (
                        (value.text is None or value.text.strip() == "")
                        and value.badge is None
                        and (value.href is None or value.href.strip() == "")
                    )
                ]

    @rx.event
    def submit_rule_set(self) -> Generator[EventSpec | None, None, None]:
        """Convert the fields to a rule set and submit it to the backend."""
        if self.entity_type is None:
            self.reset()
            return
        self.clean_up_editor_values()
        try:
            rule_set = transform_fields_to_rule_set(self.entity_type, self.fields)
        except ValidationError as exc:
            self.validation_messages = transform_validation_error_to_messages(exc)
            return
        connector = BackendApiConnector.get()
        try:
            connector.create_rule_set(rule_set)
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error submitting rule set", exc.response.text
            )
            return
        # clear cache to show edits in the UI
        resolve_identifier.cache_clear()
        yield rx.toast.success(
            title="Saved",
            description=f"{self.entity_type} was saved successfully.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )
        self.refresh()

    @rx.event
    def clear_validation_messages(self) -> None:
        """Clear all validation messages."""
        self.validation_messages.clear()

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
    def add_additive_value(self, field_name: str) -> None:
        """Add an additive rule to the given field."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values.append(EditorValue())

    @rx.event
    def remove_additive_value(self, field_name: str, index: int) -> None:
        """Remove an additive rule from the given field."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values.pop(index)

    @rx.event
    def set_entity_type(self, entity_type: str) -> None:
        """Change the selected entity type to create."""
        self.entity_type = entity_type
        self.refresh()

    @rx.event
    def set_text_value(self, field_name: str, index: int, value: str | None) -> None:
        """Set the text attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].text = value

    @rx.event
    def set_badge_value(self, field_name: str, index: int, value: str | None) -> None:
        """Set the badge attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].badge = value

    @rx.event
    def set_href_value(self, field_name: str, index: int, value: str | None) -> None:
        """Set an external href on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].href = value
        primary_source.editor_values[index].external = True
