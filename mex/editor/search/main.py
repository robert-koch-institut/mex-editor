import reflex as rx

from mex.common.types import IDENTIFIER_PATTERN
from mex.editor.component_option_helper import (
    build_pagination_options,
)
from mex.editor.layout import page
from mex.editor.search.models import (
    ReferenceFieldIdentifierFilter,
    SearchPrimarySource,
)
from mex.editor.search.state import SearchState, full_refresh
from mex.editor.search.value_label_select import value_label_select
from mex.editor.search_results_component import (
    SearchResultsComponentOptions,
    SearchResultsListItemOptions,
    SearchResultsListOptions,
    search_results_component,
)


def search_input() -> rx.Component:
    """Render a search input element that will trigger the results to refresh."""
    return rx.card(
        rx.form.root(
            rx.hstack(
                rx.input(
                    default_value=SearchState.query_string,
                    max_length=100,
                    name="query_string",
                    placeholder=SearchState.label_search_input_placeholder,
                    style=rx.Style(
                        {
                            "--text-field-selection-color": "",
                            "--text-field-focus-color": "transparent",
                            "--text-field-border-width": "calc(1px * var(--scaling))",
                            "boxShadow": (
                                "inset 0 0 0 var(--text-field-border-width) transparent"
                            ),
                        }
                    ),
                    tab_index=1,
                    type="text",
                    custom_attrs={"data-testid": "search-input"},
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("search"),
                    type="submit",
                    variant="surface",
                    disabled=SearchState.is_loading,
                    custom_attrs={"data-testid": "search-button"},
                ),
                width="100%",
            ),
            on_submit=[SearchState.handle_submit, *full_refresh],
        ),
        style=rx.Style(width="100%"),
    )


def entity_type_choice(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=[
            SearchState.set_entity_type(choice[0]),  # type: ignore[operator]
            *full_refresh,
        ],
        disabled=SearchState.is_loading,
    )


def entity_type_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.card(
        rx.text(
            SearchState.label_entitytype_filter_title,
            style=rx.Style(
                marginBottom="var(--space-4)",
                userSelect="none",
            ),
        ),
        rx.vstack(
            rx.foreach(
                SearchState.entity_types,
                entity_type_choice,
            ),
            custom_attrs={"data-testid": "entity-types"},
        ),
        style=rx.Style(width="100%"),
    )


def primary_source_choice(choice: tuple[str, SearchPrimarySource]) -> rx.Component:
    """Render a single checkbox for filtering by primary source."""
    return rx.checkbox(
        choice[1].title,
        checked=choice[1].checked,
        on_change=[
            SearchState.set_had_primary_source(choice[0]),  # type: ignore[operator]
            *full_refresh,
        ],
        disabled=SearchState.is_loading,
        custom_attrs={"data-testid": f"primary-source-filter-{choice[0]}"},
    )


def primary_source_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by primary source."""
    return rx.vstack(
        rx.foreach(
            SearchState.had_primary_sources,
            primary_source_choice,
        ),
        custom_attrs={"data-testid": "primary-source-filter"},
        style=rx.Style(width="100%"),
    )


def reference_field_filter_identifier(
    identifier: ReferenceFieldIdentifierFilter, index: int
) -> rx.Component:
    """Render input and remove button for given reference field filter identifier."""
    return rx.vstack(
        rx.hstack(
            rx.input(
                value=identifier.value,
                on_change=[
                    SearchState.set_reference_field_filter_identifier(index),  # type: ignore[operator]
                    *full_refresh,
                ],
                required=True,
                pattern=IDENTIFIER_PATTERN,
                class_name=rx.cond(identifier.validation_msg, "bg-tomato-500", ""),
                custom_attrs={"data-testid": f"reference-field-filter-id-{index}"},
                width="80%",
            ),
            rx.button(
                rx.icon("circle-minus"),
                variant="surface",
                color_scheme="gray",
                on_click=[
                    SearchState.remove_reference_field_filter_identifier(index),  # type: ignore[operator]
                    *full_refresh,
                ],
                custom_attrs={
                    "data-testid": f"reference-field-filter-remove-id-{index}"
                },
            ),
            spacing="1",
            style=rx.Style(width="100%"),
        ),
        rx.text(
            identifier.validation_msg,
            class_name="text-tomato-500",
        ),
        style=rx.Style(width="100%"),
    )


def reference_field_filter() -> rx.Component:
    """Render dropdown and text inputs for reference filtering the search result."""
    return rx.vstack(
        rx.hstack(
            value_label_select(
                items=SearchState.all_fields_for_entity_types,
                value=SearchState.reference_field_filter.field,
                placeholder=SearchState.label_reference_field_filter_placeholder,
                on_change=[
                    SearchState.set_reference_filter_field,
                    *full_refresh,
                ],
                width="80%",
                custom_attrs={"data-testid": "reference-field-filter-field"},
            ),
            rx.button(
                rx.icon("x"),
                variant="surface",
                color_scheme="gray",
                on_click=[
                    SearchState.set_reference_filter_field(""),  # type: ignore[operator]
                    *full_refresh,
                ],
            ),
            spacing="1",
            style=rx.Style(width="100%"),
        ),
        rx.foreach(
            SearchState.reference_field_filter.identifiers,
            reference_field_filter_identifier,
        ),
        rx.hstack(
            rx.button(
                rx.icon("circle-plus"),
                rx.text(SearchState.label_reference_field_filter_add),
                variant="surface",
                color_scheme="gray",
                on_click=[
                    SearchState.add_reference_field_filter_identifier,
                ],
                custom_attrs={"data-testid": "reference-field-filter-add-id"},
            ),
        ),
        custom_attrs={"data-testid": "reference-field-filter"},
    )


def reference_filter_tab() -> rx.Component:
    """Renders tab list for reference filtering.

    Containing two tabs for dynamic filtering and filtering by primary source.

    Returns:
        The tab list component containing two tabs.
    """
    return rx.card(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    SearchState.label_reference_filter_dynamic_tab,
                    value="dynamic",
                    custom_attrs={
                        "data-testid": "reference-filter-strategy-dynamic-tab"
                    },
                ),
                rx.tabs.trigger(
                    SearchState.label_reference_filter_primarysource_tab,
                    value="had_primary_source",
                    custom_attrs={
                        "data-testid": (
                            "reference-filter-strategy-had-primary-source-tab"
                        )
                    },
                ),
                style=rx.Style(marginBottom="1rem"),
            ),
            rx.tabs.content(
                reference_field_filter(),
                value="dynamic",
            ),
            rx.tabs.content(
                primary_source_filter(),
                value="had_primary_source",
            ),
            default_value="dynamic",
            value=f"{SearchState.reference_filter_strategy}",
            on_change=[
                SearchState.set_reference_filter_strategy,
                *full_refresh,
            ],
            disabled=SearchState.is_loading,
        ),
        style=rx.Style(width="100%"),
    )


def sidebar() -> rx.Component:
    """Render sidebar with a search input and checkboxes for filtering entity types."""
    return rx.vstack(
        search_input(),
        entity_type_filter(),
        reference_filter_tab(),
        spacing="4",
        align="stretch",
        custom_attrs={"data-testid": "search-sidebar"},
        style=rx.Style(width="25%"),
    )


def search_results() -> rx.Component:
    """Render the search results with a summary, result list, and pagination."""
    return rx.cond(
        SearchState.is_loading,
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(
                marginTop="var(--space-6)",
                width="100%",
            ),
        ),
        search_results_component(
            SearchState.results,
            SearchResultsComponentOptions(
                summary_text=SearchState.label_result_summary_format,
                list_options=SearchResultsListOptions(
                    item_options=SearchResultsListItemOptions(enable_title_href=True)
                ),
                pagination_options=build_pagination_options(
                    SearchState,
                    SearchState.push_search_params,  # type: ignore[arg-type]
                ),
            ),
            style=rx.Style(flex=1),
        ),
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.hstack(
            sidebar(),
            search_results(),
            spacing="4",
            style=rx.Style(flex=1),
        )
    )
