import math
from collections.abc import Generator

import reflex as rx
from reflex.event import EventSpec
from reflex.state import serialize_mutable_proxy
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyExtractedModel, PaginatedItemsContainer
from mex.editor.aux_search.models import AuxNavItem, AuxResult
from mex.editor.aux_search.transform import transform_models_to_results
from mex.editor.exceptions import escalate_error
from mex.editor.state import State


class AuxState(State):
    """State management for the aux extractor search page."""

    results_transformed: list[AuxResult] = []
    results_extracted: list[AnyExtractedModel] = []
    total: int = 0
    query_string: str = ""
    current_page: int = 1
    limit: int = 50
    current_aux_provider: str = "wikidata"
    aux_provider_items: list[AuxNavItem] = [
        AuxNavItem(title="Wikidata", value="wikidata"),
        AuxNavItem(title="LDAP", value="ldap"),
        AuxNavItem(title="Orcid", value="orcid"),
    ]

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
    def change_extractor(self, value: str) -> None:
        """Change the current extractor."""
        self.current_aux_provider = value

    @rx.event
    def handle_submit(self, form_data: dict) -> Generator[EventSpec | None, None, None]:
        """Handle the form submit."""
        self.query_string = form_data["query_string"]
        return self.search()

    @rx.event
    def set_page(
        self, page_number: str | int
    ) -> Generator[EventSpec | None, None, None]:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)
        return self.search()

    @rx.event
    def go_to_previous_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the previous page."""
        return self.set_page(self.current_page - 1)

    @rx.event
    def go_to_next_page(self) -> Generator[EventSpec | None, None, None]:
        """Navigate to the next page."""
        return self.set_page(self.current_page + 1)

    @rx.event
    def import_result(self, index: int) -> Generator[EventSpec | None, None, None]:
        """Import the selected result to MEx backend."""
        connector = BackendApiConnector.get()
        try:
            model: AnyExtractedModel = serialize_mutable_proxy(
                self.results_extracted[index]
            )
            connector.ingest([model])
        except HTTPError as exc:
            yield from escalate_error(
                "backend", f"error importing {model.stemType}", exc.response.text
            )
        else:
            self.results_transformed[index].show_import_button = False
            yield rx.toast.success(
                title="Imported",
                description=f"{model.stemType} was imported successfully.",
                class_name="editor-toast",
                close_button=True,
                dismissible=True,
                duration=5000,
            )

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        """Search in aux-extractor for items based on the query string."""
        if self.query_string == "":
            return
        connector = BackendApiConnector.get()
        try:
            # TODO(HS): use proper connector method when available (stop-gap MX-1762)
            response = connector.request(
                method="GET",
                endpoint=self.current_aux_provider,
                params={
                    "q": self.query_string,
                    "offset": str((self.current_page - 1) * self.limit),
                    "limit": str(self.limit),
                },
            )
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error fetching items", exc.response.text
            )
        else:
            yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            container = PaginatedItemsContainer[AnyExtractedModel].model_validate(
                response
            )
            self.results_extracted = container.items
            self.results_transformed = transform_models_to_results(container.items)
            self.total = len(self.results_transformed)

    @rx.event
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search page."""
        self.reset()
        return self.search()
