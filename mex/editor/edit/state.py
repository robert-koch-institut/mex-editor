import reflex as rx

from mex.editor.models import EditorValue
from mex.editor.rules.state import RuleState
from mex.editor.rules.transform import transform_fields_to_title


class EditState(RuleState):
    """State for the edit component."""

    item_title: list[EditorValue] = []

    @rx.event
    def load_item_title(self) -> None:
        """Set the item title based on field values."""
        if self.stem_type:
            self.item_title = transform_fields_to_title(self.stem_type, self.fields)
