import reflex as rx

from mex.editor.layout import page
from mex.editor.search.state import SearchResult, SearchState


def search_result(result: SearchResult) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(
        rx.link(
            result.preview,
            href=f"/item/{result.identifier}",
        ),
        style={"width": "80%"},
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.container(
            rx.vstack(
                rx.foreach(
                    SearchState.results,
                    search_result,
                ),
            ),
            on_mount=SearchState.refresh,
        ),
    )
