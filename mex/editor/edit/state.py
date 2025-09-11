from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec

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

    @rx.var
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

    def disable_all_primary_source_and_editor_values(self) -> EventSpec:
        """Disable all primary source and editor values."""
        for field in self.fields:
            for ps in field.primary_sources:
                ps.enabled = False
                for value in ps.editor_values:
                    value.enabled = False
        return State.set_current_page_has_changes(True)
