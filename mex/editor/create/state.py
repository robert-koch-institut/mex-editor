import reflex as rx

from mex.common.models import RULE_SET_REQUEST_CLASSES
from mex.editor.rules.state import RuleState


class CreateState(RuleState):
    """State for the create component."""

    available_stem_types: list[str] = [r.stemType for r in RULE_SET_REQUEST_CLASSES]

    @rx.event
    def set_stem_type(
        self, stem_type: str
    ) -> None:  # Generator[EventSpec, None, None]:
        """Set the stem type."""
        self.stem_type = stem_type

    @rx.event
    def reset_stem_type(self) -> None:  # Generator[EventSpec, None, None]:
        """Set the stem type to its default."""
        self.stem_type = RULE_SET_REQUEST_CLASSES[0].stemType

    @rx.var
    def has_local_draft(self) -> bool:
        """Indicates if a local draft is existing.

        Returns:
            bool: Returns true if a local draft exists; otherwise false.
        """
        return bool(self.draft_id) and self.draft_id in self.drafts
