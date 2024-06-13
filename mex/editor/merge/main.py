import reflex as rx

from mex.editor.layout import page


def index() -> rx.Component:
    """Return the index for the merge component."""
    return page("merge", "merge that")
