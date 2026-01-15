from collections.abc import Generator, Iterable

import reflex as rx
from reflex.app import EventSpec
from reflex.event import EventType
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.components import (
    PaginationOptions,
    icon_by_stem_type,
    pagination_abstract,
    render_additional_titles,
    render_title,
    render_value,
)
from mex.editor.exceptions import escalate_error
from mex.editor.label_var import label_var
from mex.editor.layout import custom_focus_script
from mex.editor.locale_service import LocaleService
from mex.editor.models import EditorValue
from mex.editor.pagination_state_mixin import PaginationStateMixin
from mex.editor.search.models import ReferenceDialogSearchResult
from mex.editor.search.transform import transform_models_to_dialog_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class SearchReferenceDialogState(State, PaginationStateMixin):
    """State for the search reference dialog."""

    limit = 10
    user_query: str = ""
    user_reference_types: list[str] = []

    results: list[ReferenceDialogSearchResult] = []
    expanded_properties: list[str] = []
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

    @rx.var
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
    def toggle_expand_properties(self, identifier: str) -> None:
        """Toggle if all properties are visible for given identifier."""
        if identifier in self.expanded_properties:
            self.expanded_properties.remove(identifier)
        else:
            self.expanded_properties.append(identifier)

    @rx.event
    def cleanup_state_on_dialog_close(self, is_open: bool) -> None:  # noqa: FBT001
        """Cleanup dialog state when closed to address ComponentState bug."""
        if not is_open:
            self.user_query = ""
            self.user_reference_types = []
            self.results = []
            self.expanded_properties = []
            self.reset_pagination()  # type: ignore[operator]

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results:
            for value in [*result.preview, *result.title, *result.all_properties]:
                if value.identifier and not value.text:
                    async with self:
                        await resolve_editor_value(value)

    @rx.event
    def handle_submit(self, form_data: dict) -> Generator[EventSpec | None, None, None]:
        """Handle form submit by sync values and start search."""
        self.user_query = str(form_data.get("query", ""))
        self.user_reference_types = [
            value
            for key, value in form_data.items()
            if str(key).startswith("reference_type")
        ]

        yield SearchReferenceDialogState.search  # type: ignore[misc]

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        """Search for entities by query and reference_types."""
        if self.is_loading:
            return
        connector = BackendApiConnector.get()

        self.is_loading = True
        yield None
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

    def render_properties(props: list[EditorValue]) -> rx.Component:
        return rx.hstack(
            rx.foreach(
                props,
                render_value,
            ),
            style=rx.Style(
                color="var(--gray-12)",
                fontWeight="var(--font-weight-light)",
            ),
            wrap="wrap",
        )

    def render_result_item(item: ReferenceDialogSearchResult) -> rx.Component:
        """Render a single merged item search result."""
        return rx.card(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        icon_by_stem_type(
                            item.stem_type,
                            size=22,
                            style=rx.Style(color=rx.color("accent", 11)),
                        ),
                        render_title(item.title[0]),
                        render_additional_titles(item.title[1:]),
                        rx.button(
                            rx.icon(
                                rx.cond(
                                    SearchReferenceDialogState.expanded_properties.contains(  # type: ignore[attr-defined]
                                        item.identifier
                                    ),
                                    "minimize_2",
                                    "maximize_2",
                                ),
                                style=rx.Style(width="1em", height="1em"),
                            ),
                            color_scheme="gray",
                            variant="surface",
                            size="1",
                            on_click=SearchReferenceDialogState.toggle_expand_properties(
                                item.identifier
                            ),  # type: ignore[operator]
                        ),
                    ),
                    rx.cond(
                        SearchReferenceDialogState.expanded_properties.contains(  # type: ignore[attr-defined]
                            item.identifier
                        ),
                        render_properties(item.all_properties),
                        render_properties(item.preview),
                    ),
                    style=rx.Style(width="100%", flex="1", min_width="0"),
                ),
                rx.dialog.close(
                    rx.button(
                        SearchReferenceDialogState.label_results_select_button,
                        on_click=on_identifier_selected(item.identifier),  # type: ignore[misc]
                        custom_attrs={
                            "data-testid": f"{component_id_prefix}-result-select-button"
                        },
                    ),
                    style=rx.Style(flex="0 0 auto"),
                ),
                align="center",
            ),
            class_name="search-result-card",
            custom_attrs={
                "data-testid": f"{component_id_prefix}-result-{item.identifier}"
            },
            style=rx.Style(width="100%", flex="1 0 auto", min_height="0"),
        )

    def render_result() -> rx.Component:
        return rx.cond(
            SearchReferenceDialogState.is_loading,
            rx.center(rx.spinner()),
            rx.cond(
                SearchReferenceDialogState.results,
                rx.vstack(
                    rx.foreach(SearchReferenceDialogState.results, render_result_item),
                    style=rx.Style(overflow="auto", max_height="50vh"),
                    custom_attrs={
                        "data-testid": f"{component_id_prefix}-search-results"
                    },
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
        return rx.fragment(
            rx.form(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.input(
                                value=SearchReferenceDialogState.user_query,
                                on_change=SearchReferenceDialogState.set_user_query,  # type: ignore[attr-defined]
                                custom_attrs={
                                    "data-focusme": "",
                                    "data-testid": f"{component_id_prefix}-query-input",
                                },
                                placeholder=SearchReferenceDialogState.label_query_placeholder,
                                name="query",
                                disabled=SearchReferenceDialogState.is_loading,
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
                                id=f"{component_id_prefix}-form-submit-button",
                                custom_attrs={"data-testid": "search-button"},
                            ),
                            style=rx.Style(flex="1"),
                        ),
                        rx.spacer(),
                        pagination_abstract(pagination_opts, style=rx.Style(flex="0")),
                        align="stretch",
                        justify="between",
                        style=rx.Style(width="100%"),
                        wrap="wrap",
                    ),
                    rx.el.div(
                        rx.foreach(
                            reference_types,
                            lambda value, index: rx.checkbox(
                                value,
                                name=f"reference_type[{index}]",
                                value=value,
                                checked=True,
                            ),
                        ),
                        style=rx.Style(display="None"),
                    ),
                ),
                id=f"{component_id_prefix}-form",
                on_submit=[
                    SearchReferenceDialogState.handle_submit,
                    SearchReferenceDialogState.resolve_identifiers,
                ],
            ),
            rx.script(
                f"setTimeout(() => document.getElementById('{component_id_prefix}-form-submit-button').click())"  # noqa: E501
            ),
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
                rx.el.br(),
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
        ),
        on_open_change=SearchReferenceDialogState.cleanup_state_on_dialog_close,
    )
