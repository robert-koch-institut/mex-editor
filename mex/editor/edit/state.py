from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec

from mex.editor.label_var import label_var
from mex.editor.rules.state import RuleState
from mex.editor.state import State


class EditState(RuleState):
    """State for the edit component."""

    @rx.event
    def show_submit_success_toast_on_redirect(self) -> Generator[EventSpec, None, None]:
        """Show a success toast when the saved param is set."""
        if "saved" in self.router.page.params:
            yield EditState.show_submit_success_toast
            params = self.router.page.params.copy()
            params.pop("saved")
            if event := self.push_url_params(params):
                yield event

    @rx.var(cache=False)
    def any_primary_source_or_editor_value_enabled(self) -> bool:
        """Determine if any primary source or editor value is enabled.

        Returns:
            bool: Return true if any primary source or editor value is enabled,
            otherwise false.
        """
        return any(
            ps.enabled or any(value.enabled for value in ps.editor_values)
            for field in self.fields
            for ps in field.primary_sources
        )

    def toggle_all_primary_source_and_editor_values(self) -> EventSpec:
        """Toggle all primary source and editor values."""
        any_enabled = self.any_primary_source_or_editor_value_enabled
        new_state = not any_enabled
        for field in self.fields:
            for ps in field.primary_sources:
                ps.enabled = new_state
                for value in ps.editor_values:
                    value.enabled = new_state
        return State.set_current_page_has_changes(True)  # type: ignore[misc]

    @label_var(label_id="edit.toggle_all")
    def label_toggle_all(self) -> None:
        """Label for toggle_all."""
