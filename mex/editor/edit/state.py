import json

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import RULE_SET_RESPONSE_CLASSES_BY_NAME
from mex.common.transform import ensure_postfix
from mex.editor.edit.models import EditableField
from mex.editor.edit.transform import (
    transform_fields_to_rule_set,
    transform_models_to_fields,
)
from mex.editor.models import FixedValue
from mex.editor.state import State
from mex.editor.transform import (
    transform_models_to_stem_type,
    transform_models_to_title,
)


class EditState(State):
    """State for the edit component."""

    fields: list[EditableField] = []
    item_title: list[FixedValue] = []
    stem_type: str | None = None
    preview: list[EditableField] = []
    preview_errors: list[str] = []
    debug_editor_fields: str = ""
    debug_rule_set: str = ""
    editable_fields: list[str] = []

    def refresh(self) -> EventSpec | None:
        """Refresh the edit page."""
        self.reset()
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            extracted_data = connector.fetch_extracted_items(
                None,
                self.item_id,
                None,
                0,
                100,
            )
        except HTTPError as exc:
            self.reset()
            logger.error(
                "backend error fetching extracted items: %s",
                exc.response.text,
                exc_info=False,
            )
            return rx.toast.error(
                exc.response.text,
                duration=5000,
                close_button=True,
                dismissible=True,
            )
        self.item_title = transform_models_to_title(extracted_data.items)
        self.stem_type = transform_models_to_stem_type(extracted_data.items)
        try:
            rule_set = connector.get_rule_set(self.item_id)
        except HTTPError:
            rule_set_class = RULE_SET_RESPONSE_CLASSES_BY_NAME[
                ensure_postfix(self.stem_type, "RuleSetRequest")
            ]
            rule_set = rule_set_class(stableTargetId=self.item_id)
        self.fields = transform_models_to_fields(
            *extracted_data.items,
            rule_set.additive,
            subtractive=rule_set.subtractive,
            preventive=rule_set.preventive,
        )
        return None

    def refresh_preview(self) -> None:
        """Return a preview of the active item."""
        if (stem_type := self.stem_type) is None:
            self.reset()
            return
        self.preview.clear()
        self.preview_errors.clear()
        self.debug_editor_fields = json.dumps(
            [field.dict() for field in self.fields],
            indent=2,
            ensure_ascii=False,
        )
        rule_set = transform_fields_to_rule_set(
            stem_type,
            self.fields,
        )
        self.debug_rule_set = json.dumps(
            rule_set.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
        connector = BackendApiConnector.get()
        try:
            response = connector.preview_merged_item(self.item_id, rule_set)
        except HTTPError as exc:
            self.preview_errors = [
                ": ".join(x for x in (".".join(item["loc"]), item["msg"]) if x)
                for item in exc.response.json()["debug"]["errors"]
            ]
            logger.error(
                "backend error generating merged preview: %s",
                exc.response.text,
                exc_info=False,
            )
        else:
            self.preview = transform_models_to_fields(response)

    def submit_rule_set(self) -> EventSpec | None:
        """Convert the fields to a rule set and submit it to the backend."""
        if (stem_type := self.stem_type) is None:
            self.reset()
            return None
        rule_set = transform_fields_to_rule_set(stem_type, self.fields)
        connector = BackendApiConnector.get()
        try:
            # TODO(ND): use proper connector method
            connector.request(
                method="PUT",
                endpoint=f"rule-set/{self.item_id}",
                payload=rule_set,
            )
        except HTTPError as exc:
            self.reset()
            logger.error(
                "backend error submitting rule set: %s",
                exc.response.text,
                exc_info=False,
            )
            return rx.toast.error(
                exc.response.text,
                duration=5000,
                close_button=True,
                dismissible=True,
            )
        return rx.toast.success("Saved", duration=2000)

    def toggle_primary_source(self, field_name: str, href: str, enabled: bool) -> None:
        """Toggle the `enabled` flag of a primary source."""
        for field in self.fields:
            if field.name == field_name:
                for primary_source in field.primary_sources:
                    if primary_source.name.href == href:
                        primary_source.enabled = enabled

    def toggle_field_value(self, field_name: str, value: object, enabled: bool) -> None:
        """Toggle the `enabled` flag of a field value."""
        for field in self.fields:
            if field.name == field_name:
                for primary_source in field.primary_sources:
                    for editor_value in primary_source.editor_values:
                        if editor_value == value:
                            editor_value.enabled = enabled
