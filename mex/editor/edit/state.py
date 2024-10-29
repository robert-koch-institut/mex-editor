import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.editor.edit.models import EditableField
from mex.editor.edit.transform import transform_models_to_fields
from mex.editor.models import FixedValue
from mex.editor.state import State
from mex.editor.transform import transform_models_to_title


class EditState(State):
    """State for the edit component."""

    fields: list[EditableField] = []
    item_title: list[FixedValue] = []

    def refresh(self) -> EventSpec | None:
        """Refresh the edit page."""
        self.reset()
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_extracted_items(
                None,
                self.item_id,
                None,
                0,
                100,
            )
        except HTTPError as exc:
            self.reset()
            logger.error("backend error: %s", exc.response.text, exc_info=False)
            return rx.toast.error(
                exc.response.text,
                duration=5000,
                close_button=True,
                dismissible=True,
            )
        self.item_title = transform_models_to_title(response.items)
        self.fields = transform_models_to_fields(response.items)
        return None
