from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.models import EditorValue
from mex.editor.rules.state import RuleState
from mex.editor.transform import transform_models_to_title


class EditState(RuleState):
    """State for the edit component."""

    item_title: list[EditorValue] = []

    @rx.event
    def load_item_title(self) -> None:
        """Set the item title based on field values."""
        if self.item_id:
            connector = BackendApiConnector.get()
            # TODO(ND): use proper connector method when available (stop-gap MX-1984)
            container = connector.fetch_preview_items(identifier=self.item_id)
            self.item_title = transform_models_to_title(container.items)

    @rx.event
    def show_submit_success_toast_on_redirect(self) -> Generator[EventSpec, None, None]:
        """Show a success toast when the saved param is set."""
        if "saved" in self.router.page.params:
            yield self.show_submit_success_toast()
            params = self.router.page.params.copy()
            params.pop("saved")
            yield self.push_url_params(params)

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

    def disable_all_primary_source_and_editor_values(self) -> None:
        """Disable all primary source and editor values."""
        for field in self.fields:
            for ps in field.primary_sources:
                ps.enabled = False
                for value in ps.editor_values:
                    value.enabled = False
