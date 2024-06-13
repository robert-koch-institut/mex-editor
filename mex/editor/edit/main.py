import reflex as rx

from mex.editor.layout import page


class State(rx.State):
    """State for the edit component."""

    @rx.var
    def item_id(self) -> str:
        """Return the current item id."""
        return str(self.router.page.params["item_id"])


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page("edit", f"edit {State.item_id}")
