import math
from typing import TYPE_CHECKING, Annotated

import reflex as rx
from pydantic import Field
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import MExError
from mex.common.models import MERGED_MODEL_CLASSES, MergedPrimarySource
from mex.common.transform import ensure_prefix
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import SearchPrimarySource, SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.types import EventGenerator
from mex.editor.utils import resolve_editor_value

if TYPE_CHECKING:
    from reflex.istate.data import RouterData


class SearchState(State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: Annotated[int, Field(ge=0)] = 0
    query_string: Annotated[str, Field(max_length=1000)] = ""
    entity_types: dict[str, bool] = {k.stemType: False for k in MERGED_MODEL_CLASSES}
    had_primary_sources: dict[str, SearchPrimarySource] = {}
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    is_loading: bool = True

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
    def page_selection(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / self.limit))]

    @rx.var(cache=False)
    def disable_page_selection(self) -> bool:
        """Whether the page selection in the pagination should be disabled."""
        return math.ceil(self.total / self.limit) == 1

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
        for primary_source_identifier in had_primary_source_params:
            self.had_primary_sources[primary_source_identifier].checked = True

    @rx.event
    def push_search_params(self) -> EventGenerator:
        """Push a new browser history item with updated search parameters."""
        yield self.push_url_params(
            {
                "q": self.query_string,
                "page": self.current_page,
                "entityType": [k for k, v in self.entity_types.items() if v],
                "hadPrimarySource": [
                    k for k, v in self.had_primary_sources.items() if v.checked
                ],
            },
        )

    @rx.event
    def set_entity_type(
        self,
        index: str,
        value: bool,  # noqa: FBT001
    ) -> None:
        """Set the entity type for filtering and refresh the results."""
        self.entity_types[index] = value

    @rx.event
    def set_had_primary_source(
        self,
        index: str,
        value: bool,  # noqa: FBT001
    ) -> None:
        """Set the entity type for filtering and refresh the results."""
        self.had_primary_sources[index].checked = value

    @rx.event
    def set_page(self, page_number: str | int) -> None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)

    @rx.event
    def handle_submit(self, form_data: dict) -> None:
        """Handle the form submit."""
        self.query_string = form_data["query_string"]

    @rx.event
    def go_to_first_page(self) -> None:
        """Navigate to the first page."""
        self.current_page = 1

    @rx.event
    def go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        self.current_page = self.current_page - 1

    @rx.event
    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        self.current_page = self.current_page + 1

    @rx.event
    def scroll_to_top(self) -> EventGenerator:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)

    @rx.event
    def refresh(self) -> EventGenerator:
        """Refresh the search results."""
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        entity_type = [
            ensure_prefix(k, "Merged") for k, v in self.entity_types.items() if v
        ]
        had_primary_source = [
            identifier
            for identifier, primary_source in self.had_primary_sources.items()
            if primary_source.checked
        ]
        skip = self.limit * (self.current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_string,
                entity_type=entity_type,
                reference_field="hadPrimarySource" if had_primary_source else None,
                referenced_identifier=had_primary_source,
                skip=skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results = []
            self.total = 0
            self.current_page = 1
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results = transform_models_to_results(response.items)
            self.total = response.total

    @rx.event
    def get_available_primary_sources(self) -> EventGenerator:
        """Get all available primary sources."""
        # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()
        maximum_number_of_primary_sources = 100
        try:
            primary_sources_response = connector.fetch_preview_items(
                entity_type=[MergedPrimarySource.__name__],
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
            search_primary_sources = [
                SearchPrimarySource(
                    identifier=source.identifier,
                    title=source.title[0].text or "",
                    checked=False,
                )
                for source in available_primary_sources
            ]
            self.had_primary_sources = {
                str(source.identifier): source
                for source in sorted(
                    search_primary_sources, key=lambda source: source.title.lower()
                )
            }
