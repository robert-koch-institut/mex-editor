import reflex as rx

from mex.editor.layout import page
from mex.editor.search.state import SearchState


def search_result(item: str) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(rx.text(item[:100]))


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        "search",
        rx.vstack(
            rx.hstack(
                rx.button(
                    "Search",
                    on_click=SearchState.refresh,
                ),
            ),
            rx.foreach(
                SearchState.results,
                search_result,
            ),
        ),
    )
