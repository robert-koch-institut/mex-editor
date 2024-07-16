import reflex as rx

from mex.common.backend_api.connector import BackendApiConnector


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
