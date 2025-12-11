import reflex as rx

from mex.common.models import RULE_SET_REQUEST_CLASSES
from mex.editor.label_var import label_var
from mex.editor.rules.state import RuleState


class CreateState(RuleState):
    """State for the create component."""

    available_stem_types: list[str] = [r.stemType for r in RULE_SET_REQUEST_CLASSES]

    @rx.event
    def set_stem_type(self, stem_type: str) -> None:
        """Set the stem type."""
        self.stem_type = stem_type

    @rx.event
    def reset_stem_type(self) -> None:
        """Set the stem type to its default."""
        self.stem_type = RULE_SET_REQUEST_CLASSES[0].stemType

    @label_var(label_id="create.title.create_new")
    def label_title_create_new(self) -> None:
        """Label for title.create_new."""
