import math
from collections.abc import Generator
from typing import TYPE_CHECKING, Literal

import reflex as rx
from pydantic import TypeAdapter, ValidationError
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import MExError
from mex.common.fields import REFERENCE_FIELDS_BY_CLASS_NAME
from mex.common.models import MERGED_MODEL_CLASSES, MergedPrimarySource
from mex.common.transform import ensure_prefix
from mex.common.types import Identifier
from mex.editor.constants import DEFAULT_FETCH_LIMIT, PRIMARY_SOURCE_FILTER_FETCH_LIMIT
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import (
    ReferenceFieldFilter,
    ReferenceFieldIdentifierFilter,
    SearchPrimarySource,
    SearchResult,
)
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value

if TYPE_CHECKING:
    from reflex.istate.data import RouterData


def _build_dynamic_refresh_params(reference_field_filter: ReferenceFieldFilter) -> dict:
    identifiers = [
        x for x in reference_field_filter.identifiers if not x.validation_msg
    ]
    if not reference_field_filter.field or not identifiers:
        return {"reference_field": None, "referenced_identifier": None}
    return {
        "reference_field": reference_field_filter.field,
        "referenced_identifier": [x.value for x in identifiers],
    }


def _build_had_primary_source_refresh_params(
    had_primary_sources: dict[str, SearchPrimarySource],
) -> dict:
    had_primary_source = [
        identifier
        for identifier, primary_source in had_primary_sources.items()
        if primary_source.checked
    ]
    return {
        "reference_field": "hadPrimarySource" if had_primary_source else None,
        "referenced_identifier": had_primary_source,
    }


class SearchState(State):
    """State management for the search page."""

    results: list[SearchResult] = []
    total: int = 0
    query_string: str = ""
    entity_types: dict[str, bool] = {k.stemType: False for k in MERGED_MODEL_CLASSES}

    reference_filter_strategy: Literal["had_primary_source", "dynamic"] = "dynamic"
    had_primary_sources: dict[str, SearchPrimarySource] = {}
    current_page: int = 1
    reference_field_filter: ReferenceFieldFilter = ReferenceFieldFilter(
        field="", identifiers=[]
    )
    is_loading: bool = True

    @rx.event
    def set_reference_filter_field(self, value: str) -> None:
        """Set the reference filter field used to filter references.

        Args:
            value (str): The field to use for reference filtering.
        """
        self.reference_field_filter.field = value

    @rx.event
    def set_reference_filter_strategy(
        self, value: Literal["had_primary_source", "dynamic"]
    ) -> None:
        """Set the reference filter strategy to define the filter mechanism.

        Args:
            value: The strategy used for filtering.
        """
        self.reference_filter_strategy = value

    @rx.event
    def set_reference_field_filter_identifier(self, index: int, value: str) -> None:
        """Set the reference value to filter for at a specific index.

        Args:
            index (int): Index of the identifier
            value (str): Value of the identifier
        """
        self.reference_field_filter.identifiers[index].validation_msg = None
        self.reference_field_filter.identifiers[index].value = value
        try:
            TypeAdapter(Identifier).validate_python(value)
        except ValidationError as ve:
            self.reference_field_filter.identifiers[index].validation_msg = "\n".join(
                [error["msg"] for error in ve.errors()]
            )

    @rx.event
    def remove_reference_field_filter_identifier(self, index: int) -> None:
        """Remove the reference value to filter for at a specific index.

        Args:
            index: Index of the identifier to remove.
        """
        self.reference_field_filter.identifiers.pop(index)

    @rx.event
    def add_reference_field_filter_identifier(self) -> None:
        """Add a new empty identifier."""
        self.reference_field_filter.identifiers.append(
            ReferenceFieldIdentifierFilter(value="", validation_msg=None)
        )
        SearchState.set_reference_field_filter_identifier(  # type: ignore[misc]
            len(self.reference_field_filter.identifiers) - 1, ""
        )

    @rx.var(cache=False)
    def all_fields_for_entity_types(self) -> list[str]:
        """Get all fields for the currently selected entity types filter.

        Returns:
            list[str]: The fields for the selected entity types.
        """
        selected_entity_types = [
            item[0]
            for item in list(filter(lambda item: item[1], self.entity_types.items()))
        ]

        if len(selected_entity_types) == 0:
            selected_entity_types = [item[0] for item in self.entity_types.items()]

        fields_by_type = [
            REFERENCE_FIELDS_BY_CLASS_NAME[ensure_prefix(entity_type, "Extracted")]
            for entity_type in selected_entity_types
        ]
        return sorted({f for fields in fields_by_type for f in fields})

    @rx.var(cache=False)
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var(cache=False)
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        max_page = math.ceil(self.total / DEFAULT_FETCH_LIMIT)
        return self.current_page >= max_page

    @rx.var(cache=False)
    def current_results_length(self) -> int:
        """Return the number of current search results."""
        return len(self.results)

    @rx.var(cache=False)
    def page_selection(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / DEFAULT_FETCH_LIMIT))]

    @rx.var(cache=False)
    def disable_page_selection(self) -> bool:
        """Whether the page selection in the pagination should be disabled."""
        return math.ceil(self.total / DEFAULT_FETCH_LIMIT) == 1

    @rx.event
    def load_search_params(self) -> None:
        """Load url params into the state."""
        router: RouterData = self.get_value("router")
        self.set_page(router.page.params.get("page", 1))  # type: ignore[misc]
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

        reference_filter_strategy = router.page.params.get(
            "referenceFilterStrategy", "dynamic"
        )
        self.reference_filter_strategy = (
            reference_filter_strategy
            if reference_filter_strategy in ["dynamic", "had_primary_source"]
            else "dynamic"
        )
        ref_field_identifiers = router.page.params.get("referenceIdentifier", [])
        ref_field_identifiers = (
            ref_field_identifiers
            if isinstance(ref_field_identifiers, list)
            else [ref_field_identifiers]
        )
        self.reference_field_filter = ReferenceFieldFilter(
            field=router.page.params.get("referenceField", ""),
            identifiers=[
                ReferenceFieldIdentifierFilter(value=x, validation_msg=None)
                for x in ref_field_identifiers
            ],
        )

    @rx.event
    def push_search_params(self) -> Generator[EventSpec | None, None, None]:
        """Push a new browser history item with updated search parameters."""
        yield self.push_url_params(
            {
                "q": self.query_string,
                "page": self.current_page,
                "entityType": [k for k, v in self.entity_types.items() if v],
                "referenceFilterStrategy": self.reference_filter_strategy,
                "hadPrimarySource": [
                    k for k, v in self.had_primary_sources.items() if v.checked
                ],
                "referenceField": self.reference_field_filter.field,
                "referenceIdentifier": [
                    x.value for x in self.reference_field_filter.identifiers
                ],
            }
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
    def scroll_to_top(self) -> Generator[EventSpec, None, None]:
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
    def refresh(self) -> Generator[EventSpec | None, None, None]:
        """Refresh the search results."""
        # TODO(ND): use proper connector method when available (stop-gap MX-1984)
        connector = BackendApiConnector.get()
        entity_type = [
            ensure_prefix(k, "Merged") for k, v in self.entity_types.items() if v
        ]
        filter_strategy_params = (
            _build_dynamic_refresh_params(self.reference_field_filter)
            if self.reference_filter_strategy == "dynamic"
            else _build_had_primary_source_refresh_params(self.had_primary_sources)
        )

        skip = DEFAULT_FETCH_LIMIT * (self.current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.query_string,
                entity_type=entity_type,
                skip=skip,
                limit=DEFAULT_FETCH_LIMIT,
                **filter_strategy_params,
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
    def get_available_primary_sources(self) -> Generator[EventSpec, None, None]:
        """Get all available primary sources."""
        # TODO(ND): use proper connector method when available (stop-gap MX-1984)
        connector = BackendApiConnector.get()
        try:
            primary_sources_response = connector.fetch_preview_items(
                entity_type=[ensure_prefix(MergedPrimarySource.stemType, "Merged")],
                skip=0,
                limit=PRIMARY_SOURCE_FILTER_FETCH_LIMIT,
            )
        except HTTPError as exc:
            yield from escalate_error(
                "backend", "error fetching primary sources", exc.response.text
            )
        else:
            available_primary_sources = transform_models_to_results(
                primary_sources_response.items
            )
            if len(available_primary_sources) == PRIMARY_SOURCE_FILTER_FETCH_LIMIT:
                msg = (
                    f"Cannot handle more than {PRIMARY_SOURCE_FILTER_FETCH_LIMIT} "
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


full_refresh = [
    SearchState.go_to_first_page,
    SearchState.push_search_params,
    SearchState.refresh,
    SearchState.resolve_identifiers,
]
