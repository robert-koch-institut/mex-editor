from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.label_var import label_var
from mex.editor.rules.state import RuleState


class EditState(RuleState):
    """State for the edit component."""

    is_deleting: bool = False

    @rx.event
    def delete_reset(self) -> Generator[EventSpec | None]:
        """Call the delete or reset function."""
        self.is_deleting = True
        yield None

        connector = BackendApiConnector.get()
        # TODO(FE): Use func when merge backend in
        # connector.delete_rule_set(self.item_id)
        print("DELETING RULES", self.item_id)

        if self.delete_reset_mode == "delete":
            yield rx.redirect("/")
            yield rx.toast.success(
                title=self.label_delete_rules_success_toast_title,
                description=self.label_delete_rules_success_toast_text,
                class_name="editor-toast",
                close_button=True,
                dismissible=True,
                duration=5000,
                custom_attrs={"data-testid": "delete-success-toast"},
            )
        elif self.delete_reset_mode == "reset":
            yield rx.redirect(f"/item/{self.item_id}")
            yield rx.toast.success(
                title=self.label_reset_rules_success_toast_title,
                description=self.label_reset_rules_success_toast_text,
                class_name="editor-toast",
                close_button=True,
                dismissible=True,
                duration=5000,
                custom_attrs={"data-testid": "reset-success-toast"},
            )

        self.is_deleting = False

    @rx.event
    def show_submit_success_toast_on_redirect(self) -> Generator[EventSpec]:
        """Show a success toast when the saved param is set."""
        if "saved" in self.router.page.params:
            yield EditState.show_submit_success_toast  # type: ignore[misc]
            params = self.router.page.params.copy()
            params.pop("saved")
            if event := self.push_url_params(params):
                yield event

    @rx.var(cache=False)
    def any_primary_source_or_editor_value_enabled(self) -> bool:
        """Determine if any primary source or editor value is enabled.

        Returns:
            Return true if any primary source or editor value is enabled,
            otherwise false.
        """
        return any(
            ps.enabled or any(value.enabled for value in ps.editor_values)
            for field in self.fields
            for ps in field.primary_sources
        )

    @rx.event
    def toggle_all_primary_source_and_editor_values(
        self,
    ) -> Generator[EventSpec]:
        """Toggle all primary source and editor values."""
        any_enabled = self.any_primary_source_or_editor_value_enabled
        new_state = not any_enabled
        for field in self.fields:
            for ps in field.primary_sources:
                ps.enabled = new_state
                for value in ps.editor_values:
                    value.enabled = new_state
        yield RuleState.update_local_state  # type: ignore[misc]

    @label_var(label_id="edit.toggle_all")
    def label_toggle_all(self) -> None:
        """Label for toggle_all."""

    @label_var(label_id="edit.discard_changes.button")
    def label_discard_changes_button(self) -> None:
        """Label for discard_changes.button."""

    @label_var(label_id="edit.discard_changes_dialog.title")
    def label_discard_changes_dialog_title(self) -> None:
        """Label for discard_changes_dialog.title."""

    @label_var(label_id="edit.discard_changes_dialog.description")
    def label_discard_changes_dialog_description(self) -> None:
        """Label for discard_changes_dialog.description."""

    @label_var(label_id="edit.discard_changes_dialog.cancel_button")
    def label_discard_changes_dialog_cancel_button(self) -> None:
        """Label for discard_changes_dialog.cancel_button."""

    @label_var(label_id="edit.discard_changes_dialog.discard_button")
    def label_discard_changes_dialog_discard_button(self) -> None:
        """Label for discard_changes_dialog.discard_button."""

    @label_var(label_id="edit.reset_rules.button")
    def label_reset_rules_button(self) -> None:
        """Label for reset_rules.button."""

    @label_var(label_id="edit.delete_rules.button")
    def label_delete_rules_button(self) -> None:
        """Label for delete_rules.button."""

    @label_var(label_id="edit.delete_rules.success_toast_title")
    def label_delete_rules_success_toast_title(self) -> None:
        """Label for delete_rules.success_toast_title."""

    @label_var(label_id="edit.delete_rules.success_toast_text")
    def label_delete_rules_success_toast_text(self) -> None:
        """Label for delete_rules.success_toast_text."""

    @label_var(label_id="edit.reset_rules.success_toast_title")
    def label_reset_rules_success_toast_title(self) -> None:
        """Label for reset_rules.success_toast_title."""

    @label_var(label_id="edit.reset_rules.success_toast_text")
    def label_reset_rules_success_toast_text(self) -> None:
        """Label for reset_rules.success_toast_text."""
