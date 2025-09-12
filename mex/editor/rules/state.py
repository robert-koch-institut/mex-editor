from collections.abc import Generator, Sequence
from typing import cast

import reflex as rx
from pydantic import ValidationError
from reflex.event import EventSpec
from requests import HTTPError
from starlette import status

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.merged.main import create_merged_item
from mex.common.models import (
    RULE_SET_REQUEST_CLASSES,
    RULE_SET_REQUEST_CLASSES_BY_NAME,
    RULE_SET_RESPONSE_CLASSES_BY_NAME,
    AnyExtractedModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
from mex.common.transform import ensure_postfix
from mex.common.types import Identifier, Validation
from mex.editor.exceptions import escalate_error
from mex.editor.locale_service import LocaleService
from mex.editor.models import EditorValue
from mex.editor.rules.models import (
    EditorField,
    EditorPrimarySource,
    FieldTranslation,
    ValidationMessage,
)
from mex.editor.rules.transform import (
    transform_fields_to_rule_set,
    transform_models_to_fields,
    transform_validation_error_to_messages,
)
from mex.editor.state import State
from mex.editor.transform import (
    transform_models_to_stem_type,
    transform_models_to_title,
)
from mex.editor.utils import resolve_editor_value, resolve_identifier

locale_service = LocaleService.get()


class RuleState(State):
    """Base state for the edit and create components."""

    item_id: str | None = None
    item_title: list[EditorValue] = []
    fields: list[EditorField] = []
    stem_type: str | None = None
    fields: list[EditorField] = []
    validation_messages: list[ValidationMessage] = []

    @rx.var
    def translated_fields(self) -> Sequence[FieldTranslation]:
        """Compute the translated fields based on fields and current_locale.

        Returns:
            Sequence[FieldTranslation]: Translated fields containing label and
            description translation.
        """
        if self.stem_type:
            fields = cast("list[EditorField]", self.get_value("fields"))
            return [
                FieldTranslation(
                    field=field,
                    label=locale_service.get_field_label(
                        self.current_locale, self.stem_type, field.name
                    ),
                    description=locale_service.get_field_description(
                        self.current_locale, self.stem_type, field.name
                    ),
                )
                for field in fields
            ]
        return []

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for field in self.fields:
            for primary_source in field.primary_sources:
                name = primary_source.name
                if name.identifier and not name.text:
                    async with self:
                        await resolve_editor_value(name)
                for editor_value in primary_source.editor_values:
                    if editor_value.identifier and not editor_value.text:
                        async with self:
                            await resolve_editor_value(editor_value)

    def _get_extracted_items(self) -> list[AnyExtractedModel]:
        """Get the list of extracted items the rules should apply to."""
        if self.item_id:
            connector = BackendApiConnector.get()
            extracted_items_response = connector.fetch_extracted_items(
                stable_target_id=self.item_id
            )
            return extracted_items_response.items
        return []

    def _get_rule_set(self) -> AnyRuleSetRequest | AnyRuleSetResponse:
        """Get or create a rule set request or response."""
        if self.item_id:
            connector = BackendApiConnector.get()
            try:
                return connector.get_rule_set(self.item_id)
            except HTTPError as exc:
                if (
                    exc.response.status_code == status.HTTP_404_NOT_FOUND
                    and self.stem_type
                ):
                    rule_set_response_class = RULE_SET_RESPONSE_CLASSES_BY_NAME[
                        ensure_postfix(self.stem_type, "RuleSetResponse")
                    ]
                    return rule_set_response_class(stableTargetId=self.item_id)
                raise
        if stem_type := self.stem_type:
            rule_set_request_class = RULE_SET_REQUEST_CLASSES_BY_NAME[
                ensure_postfix(stem_type, "RuleSetRequest")
            ]
        else:
            rule_set_request_class = RULE_SET_REQUEST_CLASSES[0]
        return rule_set_request_class()

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the edit or create page."""
        self.fields.clear()
        self.validation_messages.clear()
        self.item_id = self.router.page.params.get("identifier")
        try:
            extracted_items = self._get_extracted_items()
        except HTTPError as exc:
            yield from escalate_error(
                "backend", "error fetching extracted items", exc.response.text
            )
            return
        if extracted_items:
            self.stem_type = transform_models_to_stem_type(extracted_items)
        try:
            rule_set = self._get_rule_set()
        except HTTPError as exc:
            yield from escalate_error(
                "backend", "error fetching rule items", exc.response.text
            )
            return
        if rule_set:
            self.stem_type = transform_models_to_stem_type([rule_set.additive])

        if self.item_id:
            preview = create_merged_item(
                identifier=Identifier(self.item_id),
                extracted_items=extracted_items,
                rule_set=rule_set,
                validation=Validation.LENIENT,
            )
            self.item_title = transform_models_to_title([preview])

        self.fields = transform_models_to_fields(
            extracted_items,
            additive=rule_set.additive,
            subtractive=rule_set.subtractive,
            preventive=rule_set.preventive,
        )

    def _send_rule_set_request(self, rule_set: AnyRuleSetRequest) -> AnyRuleSetResponse:
        """Send the rule set to the backend."""
        connector = BackendApiConnector.get()
        if self.item_id:
            return connector.update_rule_set(self.item_id, rule_set)
        return connector.create_rule_set(rule_set)

    @rx.event
    def submit_rule_set(self) -> Generator[EventSpec | None, None, None]:
        """Convert the fields to a rule set and submit it to the backend."""
        if self.stem_type is None:
            self.reset()
            return
        try:
            rule_set_request = transform_fields_to_rule_set(self.stem_type, self.fields)
        except ValidationError as exc:
            self.validation_messages = transform_validation_error_to_messages(exc)
            return
        try:
            rule_set_response = self._send_rule_set_request(rule_set_request)
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error submitting rule set", exc.response.text
            )
            return

        yield State.set_current_page_has_changes(False)
        # clear cache to show edits in the UI
        resolve_identifier.cache_clear()
        # trigger redirect to edit page or refresh state
        if rule_set_response.stableTargetId != self.item_id:
            yield rx.redirect(f"/item/{rule_set_response.stableTargetId}/?saved")
        else:
            yield from self.refresh()
            yield self.show_submit_success_toast()

    @rx.event
    def show_submit_success_toast(self) -> EventSpec:
        """Show a toast for a successfully submitted rule-set."""
        return rx.toast.success(
            title="Saved",
            description=f"{self.stem_type} was saved successfully.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )

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
    def toggle_primary_source(
        self,
        field_name: str,
        href: str | None,
        enabled: bool,  # noqa: FBT001
    ) -> EventSpec | None:
        """Toggle the `enabled` flag of a primary source."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            if primary_source.name.href == href:
                primary_source.enabled = enabled
                return State.set_current_page_has_changes(True)
        return None

    @rx.event
    def toggle_field_value(
        self,
        field_name: str,
        value: EditorValue,
        enabled: bool,  # noqa: FBT001
    ) -> EventSpec | None:
        """Toggle the `enabled` flag of a field value."""
        for primary_source in self._get_primary_sources_by_field_name(field_name):
            for editor_value in primary_source.editor_values:
                if editor_value == value:
                    editor_value.enabled = enabled
                    return State.set_current_page_has_changes(True)

        return None

    @rx.event
    def toggle_field_value_editing(
        self,
        field_name: str,
        index: int,
    ) -> None:
        """Toggle editing of a field value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[
            index
        ].being_edited = not primary_source.editor_values[index].being_edited

    @rx.event
    def add_additive_value(self, field_name: str) -> EventSpec:
        """Add an additive rule to the given field."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values.append(EditorValue(being_edited=True))
        return State.set_current_page_has_changes(True)

    @rx.event
    def remove_additive_value(self, field_name: str, index: int) -> EventSpec:
        """Remove an additive rule from the given field."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values.pop(index)
        return State.set_current_page_has_changes(True)

    @rx.event
    def set_text_value(self, field_name: str, index: int, value: str) -> EventSpec:
        """Set the text attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].text = value
        return State.set_current_page_has_changes(True)

    @rx.event
    def set_identifier_value(
        self, field_name: str, index: int, value: str
    ) -> EventSpec:
        """Set the identifier attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].identifier = value
        primary_source.editor_values[index].href = f"/item/{value}"
        return State.set_current_page_has_changes(True)

    @rx.event
    def set_badge_value(self, field_name: str, index: int, value: str) -> EventSpec:
        """Set the badge attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].badge = value
        return State.set_current_page_has_changes(True)

    @rx.event
    def set_href_value(self, field_name: str, index: int, value: str) -> EventSpec:
        """Set an external href on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].href = value
        primary_source.editor_values[index].external = True
        return State.set_current_page_has_changes(True)
