import reflex as rx

from mex.editor.edit.state import EditState
from mex.editor.layout import page


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        "edit",
        f"edit {EditState.item_id}",
    )
