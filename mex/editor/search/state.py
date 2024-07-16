import reflex as rx

from mex.common.backend_api.connector import BackendApiConnector


class SearchState(rx.State):
    """State management for the search page."""

    results: list[str] = []
    total: int = 0

    def refresh(self) -> None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        # TODO: use a specialized merged-item search method (stop-gap MX-1581)
        response = connector.request("GET", "merged-item")
        self.results = [str(i) for i in response["items"]]
        self.total = response["total"]
