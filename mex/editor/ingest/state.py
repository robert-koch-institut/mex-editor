import math
from collections.abc import Generator
from typing import Annotated

import reflex as rx
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyExtractedModel, PaginatedItemsContainer
from mex.editor.exceptions import escalate_error
from mex.editor.ingest.models import IngestResult
from mex.editor.ingest.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class IngestState(State):
    """State management for the ingest page."""

    results_transformed: list[IngestResult] = []
    results_extracted: list[AnyExtractedModel] = []
    total: Annotated[int, Field(ge=0)] = 0
    query_string: Annotated[str, Field(max_length=1000)] = ""
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 50
    current_aux_provider: str = "ldap"
    aux_providers: list[str] = ["ldap", "orcid", "wikidata"]
    is_loading: bool = True

    @rx.var(cache=False)
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / self.limit))]

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
        return len(self.results_transformed)

    @rx.event
    def toggle_show_properties(self, index: int) -> None:
        """Toggle the show properties state."""
        self.results_transformed[index].show_properties = not self.results_transformed[
            index
        ].show_properties

    @rx.event
    def set_current_aux_provider(self, value: str) -> None:
        """Change the current aux provider."""
        self.current_aux_provider = value

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
    def ingest_result(self, index: int) -> Generator[EventSpec | None, None, None]:
        """Ingest the selected result to MEx backend."""
        connector = BackendApiConnector.get()
        try:
            model: AnyExtractedModel = serialize_mutable_proxy(
                self.results_extracted[index]
            )
            connector.ingest([model])
        except HTTPError as exc:
            yield from escalate_error(
                "backend", f"error ingesting {model.stemType}", exc.response.text
            )
        else:
            self.results_transformed[index].show_ingest_button = False
            yield rx.toast.success(
                title="Ingested",
                description=f"{model.stemType} was ingested successfully.",
                class_name="editor-toast",
                close_button=True,
                dismissible=True,
                duration=5000,
            )

    @rx.event
    def scroll_to_top(self) -> Generator[EventSpec | None, None, None]:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results_transformed:
            for value in [*result.title, *result.preview, *result.all_properties]:
                if value.identifier and not value.text:
                    async with self:
                        await resolve_editor_value(value)

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results."""
        connector = BackendApiConnector.get()
        offset = self.limit * (self.current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.request(
                method="GET",
                endpoint=self.current_aux_provider,
                params={
                    "q": self.query_string or None,
                    "offset": str(offset),
                    "limit": str(self.limit),
                },
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_transformed = []
            self.results_extracted = []
            self.total = 0
            self.current_page = 1
            yield None
            yield from escalate_error(
                "backend",
                f"error fetching {self.current_aux_provider} items",
                exc.response.text,
            )
        else:
            self.is_loading = False
            container = PaginatedItemsContainer[AnyExtractedModel].model_validate(
                response
            )
            self.results_extracted = container.items
            self.results_transformed = transform_models_to_results(container.items)
            self.total = container.total
