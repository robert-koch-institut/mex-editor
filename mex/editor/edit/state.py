from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError
from starlette import status

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import RULE_SET_RESPONSE_CLASSES_BY_NAME
from mex.common.transform import ensure_postfix
from mex.editor.edit.models import EditorField, EditorPrimarySource
from mex.editor.edit.transform import (
    transform_fields_to_rule_set,
    transform_models_to_fields,
)
from mex.editor.exceptions import escalate_error
from mex.editor.models import EditorValue
from mex.editor.state import State
from mex.editor.transform import (
    transform_models_to_stem_type,
    transform_models_to_title,
)


class EditState(State):
    """State for the edit component."""

    fields: list[EditorField] = []
    item_title: list[EditorValue] = []
    stem_type: str | None = None

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the edit page."""
        self.reset()
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            extracted_items_response = connector.fetch_extracted_items(
                query_string=None,
                stable_target_id=self.router.page.params["identifier"],
                entity_type=None,
                skip=0,
                limit=100,
            )
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error fetching extracted items", exc.response.text
            )
            return

        self.item_title = transform_models_to_title(extracted_items_response.items)
        self.stem_type = transform_models_to_stem_type(extracted_items_response.items)
        try:
            rule_set = connector.get_rule_set(self.router.page.params["identifier"])
        except HTTPError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND and self.stem_type:
                rule_set_class = RULE_SET_RESPONSE_CLASSES_BY_NAME[
                    ensure_postfix(self.stem_type, "RuleSetResponse")
                ]
                rule_set = rule_set_class(
                    stableTargetId=self.router.page.params["identifier"]
                )
            else:
                self.reset()
                yield from escalate_error(
                    "backend", "error fetching rule set", exc.response.text
                )
                return

        self.fields = transform_models_to_fields(
            extracted_items_response.items,
            additive=rule_set.additive,
            subtractive=rule_set.subtractive,
            preventive=rule_set.preventive,
        )

    @rx.event
    def submit_rule_set(self) -> Generator[EventSpec | None, None, None]:
        """Convert the fields to a rule set and submit it to the backend."""
        if self.stem_type is None:
            self.reset()
            return
        rule_set = transform_fields_to_rule_set(self.stem_type, self.fields)
        connector = BackendApiConnector.get()
        try:
            # TODO(ND): use proper connector method when available (stop-gap MX-1762)
            connector.request(
                method="PUT",
                endpoint=f"rule-set/{self.router.page.params['identifier']}",
                payload=rule_set,
            )
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error submitting rule set", exc.response.text
            )
            return
        yield rx.toast.success(
            title="Saved",
            description=f"{self.stem_type} rule-set was saved successfully.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )
        yield from self.refresh()

    def _get_primary_sources_by_field_name(
        self, field_name: str
    ) -> list[EditorPrimarySource]:
        for field in self.fields:
            if field.name == field_name:
                return field.primary_sources
        msg = f"field not found: {field_name}"
        raise ValueError(msg)

    @rx.event
    def toggle_primary_source(
        self,
        field_name: str,
        href: str | None,
        enabled: bool,
    ) -> None:
        """Toggle the `enabled` flag of a primary source."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.name.href == href:
                primary_source.enabled = enabled

    @rx.event
    def toggle_field_value(
        self,
        field_name: str,
        value: EditorValue,
        enabled: bool,
    ) -> None:
        """Toggle the `enabled` flag of a field value."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            for editor_value in primary_source.editor_values:
                if editor_value == value:
                    editor_value.enabled = enabled

    @rx.event
    def add_additive_value(self, field_name: str) -> None:
        """Add an additive rule to the given field."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.input_config:
                primary_source.editor_values.append(EditorValue())

    @rx.event
    def remove_additive_value(self, field_name: str, index: int) -> None:
        """Remove an additive rule from the given field."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.input_config:
                primary_source.editor_values.pop(index)

    @rx.event
    def set_text_value(self, field_name: str, index: int, value: str) -> None:
        """Set the text attribute on an additive editor value."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.input_config:
                primary_source.editor_values[index].text = value

    @rx.event
    def set_href_value(self, field_name: str, index: int, value: str) -> None:
        """Set an external href on an additive editor value."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.input_config:
                primary_source.editor_values[index].href = value
                primary_source.editor_values[index].external = True
