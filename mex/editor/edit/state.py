from collections.abc import Generator
from urllib.parse import parse_qs

import reflex as rx
from reflex.event import EventSpec

from mex.editor.models import EditorValue
from mex.editor.rules.state import RuleState
from mex.editor.rules.transform import transform_fields_to_title


class EditState(RuleState):
    """State for the edit component."""

    item_title: rx.Field[list[EditorValue]] = rx.field(default_factory=list)

    @rx.event
    def load_item_title(self) -> None:
        """Set the item title based on field values."""
        if self.stem_type and self.fields:
            self.item_title = transform_fields_to_title(self.stem_type, self.fields)

    @rx.event
    def show_submit_success_toast_on_redirect(self) -> Generator[EventSpec, None, None]:
        """Show a success toast when the saved param is set."""
        if "saved" in parse_qs(self.router.url.query):
            yield self.show_submit_success_toast()  # type: ignore[operator]
            params = parse_qs(self.router.url.query).copy()
            params.pop("saved")
            yield self.push_url_params(params)  # type: ignore[operator]
