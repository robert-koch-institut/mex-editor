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
            yield EditState.show_submit_success_toast
            params = self.router.page.params.copy()
            params.pop("saved")
            if event := self.push_url_params(params):
                yield event
