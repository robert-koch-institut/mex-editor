from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.edit.models import EditableField
from mex.editor.edit.transform import transform_models_to_fields
from mex.editor.state import State
from mex.editor.transform import render_model_title


class EditState(State):
    """State for the edit component."""

    fields: list[EditableField] = []
    item_title: str = ""

    def refresh(self) -> None:
        """Refresh the edit page."""
        connector = BackendApiConnector.get()
        response = connector.fetch_extracted_items(None, self.item_id, None, 0, 100)
        self.item_title = render_model_title(response.items[0])
        self.fields = transform_models_to_fields(response.items)
