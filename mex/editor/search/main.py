import reflex as rx

from mex.editor.layout import page


def index() -> rx.Component:
    """Return the index for the search component."""
    return page("search", "search here")
