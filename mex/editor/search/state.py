import reflex as rx
from pydantic import BaseModel

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyMergedModel
from mex.editor.transform import (
    render_model_preview,
    render_model_title,
)


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    title: str
    preview: str


class _BackendSearchResponse(BaseModel):
    total: int
    items: list[AnyMergedModel]


class SearchState(rx.State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: int = 0

    def refresh(self) -> None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()

        # TODO: use a specialized merged-item search method (stop-gap MX-1581)
        response = connector.request("GET", "merged-item?limit=100")
        items = _BackendSearchResponse.model_validate(response).items
        self.results = [
            SearchResult(
                identifier=item.identifier,
                title=render_model_title(item),
                preview=render_model_preview(item),
            )
            for item in items
        ]
        self.total = response["total"]
