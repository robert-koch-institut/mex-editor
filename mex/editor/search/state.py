import asyncio
import math
from collections.abc import Generator
from typing import TYPE_CHECKING, Annotated

import reflex as rx
from async_lru import alru_cache
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import MExError
from mex.common.models import (
    MERGED_MODEL_CLASSES,
    AnyPreviewModel,
    MergedPrimarySource,
    PaginatedItemsContainer,
)
from mex.common.transform import ensure_prefix
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State

if TYPE_CHECKING:
    from reflex.istate.data import RouterData


@alru_cache
async def resolve_identifier(identifier: str) -> str:
    """Resolve identifiers to human readable display values."""
    # TODO(HS): use the user auth for backend requests (stop-gap MX-1616)
    connector = BackendApiConnector.get()
    # TODO(HS): use proper connector method when available (stop-gap MX-1762)
    response = connector.request(
        method="GET",
        endpoint="preview-item",
        params={
            "identifier": identifier,
            "skip": "0",
            "limit": "1",
        },
    )
    container = PaginatedItemsContainer[AnyPreviewModel].model_validate(response)
    result, *_ = transform_models_to_results(container.items)
    return f"{result.title[0].display_text}"


class SearchState(State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: Annotated[int, Field(ge=0)] = 0
    query_string: Annotated[str, Field(max_length=1000)] = ""
    entity_types: dict[str, bool] = {k.stemType: False for k in MERGED_MODEL_CLASSES}
    available_primary_sources: list[str] = []
    had_primary_sources: dict[str, bool] = {}
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    _n_resolve_identifier_tasks: int = 0

    @rx.var(cache=False)
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var(cache=False)
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        max_page = math.ceil(self.total / self.limit)
        return self.current_page >= max_page

    @rx.var(cache=False)
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

    @rx.var(cache=False)
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / self.limit))]

    @rx.event
    def load_search_params(self) -> None:
        """Load url params into the state."""
        router: RouterData = self.get_value("router")
        self.set_page(router.page.params.get("page", 1))
        self.query_string = router.page.params.get("q", "")
        type_params = router.page.params.get("entityType", [])
        type_params = type_params if isinstance(type_params, list) else [type_params]
        self.entity_types = {
            k.stemType: k.stemType in type_params for k in MERGED_MODEL_CLASSES
        }
        had_primary_source_params = router.page.params.get("hadPrimarySource", [])
        had_primary_source_params = (
            had_primary_source_params
            if isinstance(had_primary_source_params, list)
            else [had_primary_source_params]
        )
        self.had_primary_sources = {
            p: p in had_primary_source_params for p in self.available_primary_sources
        }

    @rx.event
    def push_search_params(self) -> EventSpec | None:
        """Push a new browser history item with updated search parameters."""
        return self.push_url_params(
            q=self.query_string,
            page=self.current_page,
            entityType=[k for k, v in self.entity_types.items() if v],
            hadPrimarySource=[k for k, v in self.had_primary_sources.items() if v],
        )

    @rx.event
    def set_entity_type(self, index: str, value: bool) -> None:
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value

    @rx.event
    def set_had_primary_source(self, index: str, value: bool) -> None:
        """Set the entity type for filtering and refresh the results."""
        self.had_primary_sources[index] = value

    @rx.event
    def set_page(self, page_number: str | int) -> None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)

    @rx.event
    def go_to_first_page(self) -> None:
        """Navigate to the first page."""
        self.set_page(1)

    @rx.event
    def go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        self.set_page(self.current_page - 1)

    @rx.event
    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        self.set_page(self.current_page + 1)

    @rx.event
    def scroll_to_top(self) -> Generator[EventSpec | None, None, None]:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event(background=True)
    async def resolve_identifiers(self):
        """Resolve identifiers to human readable display values."""
        async with self:
            # check if there is already a running task
            if self._n_resolve_identifier_tasks > 0:
                return
            self._n_resolve_identifier_tasks += 1

        for result in self.results:
            for preview in result.preview:
                if preview.is_identifier and not preview.is_resolved:
                    async with self:
                        preview.display_text = await resolve_identifier(preview.text)
                        preview.is_resolved = True
                        await asyncio.sleep(0.5)

        async with self:
            self._n_resolve_identifier_tasks -= 1

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results."""
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_string,
                entity_type=[
                    ensure_prefix(k, "Merged")
                    for k, v in self.entity_types.items()
                    if v
                ],
                had_primary_source=[
                    identifier
                    for identifier, include in self.had_primary_sources.items()
                    if include
                ],
                skip=self.limit * (self.current_page - 1),
                limit=self.limit,
            )
        except HTTPError as exc:
            self.results = []
            self.total = 0
            self.current_page = 1
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.results = transform_models_to_results(response.items)
            self.total = response.total

    @rx.event
    def get_available_primary_sources(self):
        """Get all available primary sources."""
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        maximum_number_of_primary_sources = 100
        try:
            primary_sources_response = connector.fetch_preview_items(
                query_string=None,
                entity_type=[ensure_prefix(MergedPrimarySource.stemType, "Merged")],
                had_primary_source=None,
                skip=0,
                limit=100,
            )
        except HTTPError as exc:
            yield from escalate_error(
                "backend", "error fetching primary sources", exc.response.text
            )
        else:
            available_primary_sources = transform_models_to_results(
                primary_sources_response.items
            )
            if len(available_primary_sources) == maximum_number_of_primary_sources:
                msg = (
                    f"Cannot handle more than {maximum_number_of_primary_sources} "
                    "primary sources."
                )
                raise MExError(msg)
            self.available_primary_sources = [
                str(source.identifier) for source in available_primary_sources
            ]
