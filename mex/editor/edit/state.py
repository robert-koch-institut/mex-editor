import reflex as rx

from mex.editor.state import State


class EditState(State):
    """State for the edit component."""

    @rx.var
    def item_id(self) -> str:
        """Return the current item id."""
        if item_id := self.router.page.params.get("item_id"):
            return str(item_id)
        return "N/A"
