import math
from collections.abc import Generator
from typing import Any

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyExtractedModel, PaginatedItemsContainer
from mex.editor.exceptions import escalate_error
from mex.editor.ingest.models import ALL_AUX_PROVIDERS, AuxProvider, IngestResult
from mex.editor.ingest.transform import transform_models_to_results
from mex.editor.state import PaginationStateMixin, State
from mex.editor.utils import resolve_editor_value


class IngestState(State, PaginationStateMixin):
    """State management for the ingest page."""

    results_transformed: list[IngestResult] = []
    results_extracted: list[AnyExtractedModel] = []
    query_string: str = ""
    current_aux_provider: AuxProvider = AuxProvider.LDAP
    aux_providers: list[AuxProvider] = ALL_AUX_PROVIDERS
    is_loading: bool = True

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
        self.current_aux_provider = AuxProvider(value)

    @rx.event
    def handle_submit(self, form_data: dict[str, Any]) -> None:
        """Handle the form submit."""
        self.query_string = form_data["query_string"]

    @rx.event
    def reset_query_string(self) -> None:
        """Reset the query string."""
        self.query_string = ""

    @rx.event
    def ingest_result(self, index: int) -> Generator[EventSpec, None, None]:
        """Ingest the selected result to MEx backend."""
        connector = BackendApiConnector.get()
        model = self.get_value(self.results_extracted[index])  # type: ignore[arg-type]
        try:
            # TODO(ND): use the user auth for backend requests (stop-gap MX-1616)
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
    def scroll_to_top(self) -> Generator[EventSpec, None, None]:
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

    @rx.event(background=True)
    async def flag_ingested_items(self) -> None:
        """Check and flag, if any result is already ingested into backend."""
        connector = BackendApiConnector.get()
        for index, result in enumerate(self.results_transformed):
            response = connector.fetch_identities(
                identifier_in_primary_source=self.results_extracted[
                    index
                ].identifierInPrimarySource,
                had_primary_source=self.results_extracted[index].hadPrimarySource,
            )
            if len(response.items) > 0:
                async with self:
                    result.show_ingest_button = False

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results."""
        connector = BackendApiConnector.get()
        # offset = self.limit * (self.current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.request(
                method="GET",
                endpoint=self.current_aux_provider,
                params={
                    "q": self.query_string or None,
                    "offset": str(self.skip),
                    "limit": str(self.limit),
                },
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results_transformed = []
            self.results_extracted = []
            yield self.set_total(0)
            yield self.set_current_page(1)
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
            self.set_total(container.total)
