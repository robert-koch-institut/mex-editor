from collections.abc import Generator, Iterable

import reflex as rx
from reflex.event import EventSpec, EventType
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.exceptions import escalate_error
from mex.editor.label_var import label_var
from mex.editor.layout import custom_focus_script
from mex.editor.locale_service import LocaleService
from mex.editor.models import SearchResult
from mex.editor.pagination_component import (
    PaginationOptions,
    PaginationStateMixin,
    pagination,
)
from mex.editor.search.transform import transform_models_to_dialog_results
from mex.editor.search_results_component import (
    SearchResultsListItemOptions,
    SearchResultsListOptions,
    search_results_list,
)
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class SearchReferenceDialogState(State, PaginationStateMixin):
    """State for the search reference dialog."""

    limit = 10
    user_query: str = ""
    user_reference_types: list[str] = []

    results: list[SearchResult] = []
    is_loading: bool = False

    _locale_service = LocaleService.get()

    @label_var(label_id="search_reference_dialog.title")
    def label_title(self) -> None:
        """Label for title."""

    @label_var(label_id="search_reference_dialog.description")
    def label_description(self) -> None:
        """Label for description."""

    @label_var(label_id="search_reference_dialog.description.valid_types")
    def label_description_valid_types(self) -> None:
        """Label for description.valid_types."""

    @label_var(label_id="search_reference_dialog.query.placeholder")
    def label_query_placeholder(self) -> None:
        """Label for query.placeholder."""

    @label_var(
        label_id="search_reference_dialog.results.none_found_format",
        deps=["user_query"],
    )
    def label_results_none_found_format(self) -> list[str]:
        """Label for results.none_found_format."""
        return [self.user_query]

    @label_var(label_id="search_reference_dialog.results.select_button")
    def label_results_select_button(self) -> None:
        """Label for results.select_button."""

    @rx.var(cache=False)
    def label_user_reference_types(self) -> str:
        """Label for the reference types."""
        # TODO(FE): PLACEHOLDER - translate reference types when doin MX-2092
        dummy_translation = self._locale_service.get_field_label(
            self.current_locale, "", "contact"
        )
        result = [
            f"{self.current_locale}: {x} ({dummy_translation})"
            for x in self.user_reference_types
        ]
        return "|".join(result)

    @rx.event
    def toggle_show_all_properties(self, item: SearchResult, index: int) -> None:
        """Toggle if all properties are visible for given identifier."""
        self.results[index].show_all_properties = not item.show_all_properties

    @rx.event
    def cleanup_state_on_dialog_close(self, is_open: bool) -> None:  # noqa: FBT001
        """Cleanup dialog state when closed to address ComponentState bug."""
        if not is_open:
            self.user_query = ""
            self.user_reference_types = []
            self.results = []
            self.reset_pagination()  # type: ignore[operator]

    @rx.event
    def set_user_query(self, value: str) -> None:
        """Set the user query value."""
        self.user_query = value

    @rx.event
    def set_user_reference_types(self, value: list[str]) -> None:
        """Set the user reference type value."""
        self.user_reference_types = value

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results:
            for value in [*result.preview, *result.title, *result.all_properties]:
                if value.identifier and not value.text:
                    async with self:
                        await resolve_editor_value(value)

    @rx.event
    def search(self) -> Generator[EventSpec | None]:
        """Search for entities by query and reference_types."""
        if self.is_loading:
            return

        self.is_loading = True
        yield None
        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_preview_items(
                query_string=self.user_query,
                entity_type=self.user_reference_types,
                skip=self.skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results = []
            self.total = 0
            yield SearchReferenceDialogState.set_current_page(1)  # type: ignore[operator]
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results = transform_models_to_dialog_results(response.items)
            yield SearchReferenceDialogState.set_total(response.total)  # type: ignore[operator]


def search_reference_dialog(
    on_identifier_selected: EventType[str],
    reference_types: rx.Var[Iterable[str]] | Iterable[str],
    field_label: rx.Var[str] | str | None = None,
) -> rx.Component:
    """Create a button that opens a dialog to search for references."""
    pagination_opts = PaginationOptions.create(
        SearchReferenceDialogState, SearchReferenceDialogState.search
    )
    component_id_prefix = "search-reference-dialog"

    def render_result() -> rx.Component:
        def render_select_button(item: SearchResult, _: int) -> rx.Component:
            return rx.dialog.close(
                rx.button(
                    SearchReferenceDialogState.label_results_select_button,
                    on_click=on_identifier_selected(item.identifier),  # type: ignore[misc]
                    custom_attrs={
                        "data-testid": f"{component_id_prefix}-result-select-button"
                    },
                ),
                style=rx.Style(margin_left="auto"),
            )

        return rx.cond(
            SearchReferenceDialogState.is_loading,
            rx.center(rx.spinner()),
            rx.cond(
                SearchReferenceDialogState.results,
                search_results_list(
                    SearchReferenceDialogState.results,
                    SearchResultsListOptions(
                        item_options=SearchResultsListItemOptions(
                            enable_show_all_properties=True,
                            on_toggle_show_all_properties=SearchReferenceDialogState.toggle_show_all_properties,  # type: ignore[arg-type]
                            render_title_fn=render_select_button,
                        )
                    ),
                    style=rx.Style(max_height="50vh"),
                ),
                rx.center(
                    rx.text(
                        SearchReferenceDialogState.label_results_none_found_format,
                        color_scheme="gray",
                        size="7",
                        style=rx.Style(padding="3em 0"),
                    ),
                    style=rx.Style(width="100%"),
                ),
            ),
        )

    def render_search_form() -> rx.Component:
        return rx.hstack(
            rx.form(
                rx.hstack(
                    rx.input(
                        value=SearchReferenceDialogState.user_query,
                        on_change=SearchReferenceDialogState.set_user_query,
                        custom_attrs={
                            "data-focusme": "",
                            "data-testid": f"{component_id_prefix}-query-input",
                        },
                        placeholder=SearchReferenceDialogState.label_query_placeholder,
                        name="query",
                        disabled=SearchReferenceDialogState.is_loading,
                        type="text",
                        style=rx.Style(
                            flex="1",
                            max_width="380px",
                            min_width="180px",
                        ),
                    ),
                    rx.button(
                        rx.icon("search"),
                        type="submit",
                        variant="surface",
                        disabled=SearchReferenceDialogState.is_loading,
                        custom_attrs={"data-testid": "search-button"},
                    ),
                ),
                on_submit=[
                    SearchReferenceDialogState.search,
                    SearchReferenceDialogState.resolve_identifiers,
                ],
            ),
            rx.spacer(),
            pagination(pagination_opts, style=rx.Style(flex="0")),
            align="stretch",
            justify="between",
            style=rx.Style(width="100%"),
        )

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon(
                    "search",
                    height="1rem",
                    width="1rem",
                ),
                variant="soft",
                size="1",
                custom_attrs={"data-testid": f"{component_id_prefix}-button"},
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    field_label,
                    f"{SearchReferenceDialogState.label_title} ({field_label})",
                    f"{SearchReferenceDialogState.label_title}",
                )
            ),
            rx.dialog.description(
                rx.text(
                    f"{SearchReferenceDialogState.label_description_valid_types}: "
                    f"{SearchReferenceDialogState.label_user_reference_types}",
                    as_="span",
                ),
                rx.spacer(),
                rx.text(
                    SearchReferenceDialogState.label_description,
                    as_="span",
                ),
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                render_search_form(),
                render_result(),
                align="stretch",
            ),
            custom_focus_script(),
            style=rx.Style({"max-width": "62vw !important"}),
            on_open_auto_focus=[
                SearchReferenceDialogState.set_user_query(""),  # type: ignore[operator]
                SearchReferenceDialogState.set_user_reference_types(reference_types),  # type: ignore[operator]
                SearchReferenceDialogState.search,
                SearchReferenceDialogState.resolve_identifiers,
            ],
        ),
        on_open_change=SearchReferenceDialogState.cleanup_state_on_dialog_close,
    )
