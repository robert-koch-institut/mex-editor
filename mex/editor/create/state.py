import reflex as rx

from mex.common.models import RULE_SET_REQUEST_CLASSES
from mex.editor.rules.state import LocalChanges, RuleState


class CreateState(RuleState):
    """State for the create component."""

    available_stem_types: list[str] = [r.stemType for r in RULE_SET_REQUEST_CLASSES]

    @rx.event
    def set_stem_type(
        self, stem_type: str
    ) -> None:  # Generator[EventSpec, None, None]:
        """Set the stem type."""
        self.stem_type = stem_type
        print("UPDATED STEM TYPE", self.stem_type)
        # yield RuleState.update_local_edit

    @rx.event
    def reset_stem_type(self) -> None:  # Generator[EventSpec, None, None]:
        """Set the stem type to its default."""
        self.stem_type = RULE_SET_REQUEST_CLASSES[0].stemType
        print("RESET STEM TYPE", self.stem_type)
        # yield RuleState.update_local_edit

    @rx.var
    def has_local_draft(self) -> bool:
        if self.draft_id:
            return self.draft_id in LocalChanges.parse_raw(self.local_storage).create
        return False
