import reflex as rx

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.layout import page


class SearchState(rx.State):
    """State management for the search page."""

    results: list[str] = []
    total: int = 0

    def refresh(self):
        """Refresh the search results."""
        connector = BackendApiConnector.get()
        response = connector.request("GET", "merged-item")
        self.results = [str(i) for i in response["items"]]
        self.total = response["total"]


def search_result(item: str) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(rx.text(item[:100]))


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        "search",
        rx.vstack(
            rx.button(
                "Search",
                on_click=SearchState.refresh,
            ),
            rx.card(rx.text("Total: "), rx.text(SearchState.total)),
            rx.foreach(SearchState.results, search_result),
        ),
    )
