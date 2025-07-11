import reflex as rx

from mex.common.models import RULE_SET_REQUEST_CLASSES
from mex.editor.rules.state import RuleState


class CreateState(RuleState):
    """State for the create component."""

    available_stem_types: list[str] = [r.stemType for r in RULE_SET_REQUEST_CLASSES]

    @rx.event
    def reset_stem_type(self) -> None:
        """Set the stem type to a default."""
        self.stem_type = RULE_SET_REQUEST_CLASSES[0].stemType
