from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.layout import page
from mex.editor.search.models import SearchPrimarySource, SearchResult
from mex.editor.search.state import SearchState


def search_result(result: SearchResult) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(
        rx.link(
            rx.box(
                rx.hstack(
                    rx.foreach(
                        result.title,
                        render_value,
                    )
                ),
                style={
                    "fontWeight": "var(--font-weight-bold)",
                    "overflow": "hidden",
                    "whiteSpace": "nowrap",
                },
            ),
            rx.box(
                rx.hstack(
                    rx.foreach(
                        result.preview,
                        render_value,
                    )
                ),
                style={
                    "color": "var(--gray-12)",
                    "fontWeight": "var(--font-weight-light)",
                    "textDecoration": "none",
                },
            ),
            href=f"/item/{result.identifier}",
        ),
        style={"width": "100%"},
        class_name="search-result-card",
        custom_attrs={"data-testid": f"result-{result.identifier}"},
    )


def search_input() -> rx.Component:
    """Render a search input element that will trigger the results to refresh."""
    return rx.card(
        rx.debounce_input(
            rx.input(
                rx.input.slot(
                    rx.icon("search"),
                    autofocus=True,
                    padding_left="0",
                    tab_index=1,
                ),
                placeholder="Search here...",
                value=SearchState.query_string,
                on_change=[
                    SearchState.set_query_string,
                    SearchState.go_to_first_page,
                    SearchState.push_search_params,
                    SearchState.refresh,
                    SearchState.resolve_identifiers,
                ],
                max_length=100,
                style={
                    "--text-field-selection-color": "",
                    "--text-field-focus-color": "transparent",
                    "--text-field-border-width": "calc(1px * var(--scaling))",
                    "boxShadow": (
                        "inset 0 0 0 var(--text-field-border-width) transparent"
                    ),
                },
            ),
            style={"margin": "var(--space-4) 0 var(--space-4)"},
            debounce_timeout=250,
        ),
        style={"width": "100%"},
    )


def entity_type_choice(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=[
            SearchState.set_entity_type(choice[0]),
            SearchState.go_to_first_page,
            SearchState.push_search_params,
            SearchState.refresh,
            SearchState.resolve_identifiers,
        ],
    )


def entity_type_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.card(
        rx.text("entityType", margin_bottom="0.5em"),
        rx.vstack(
            rx.foreach(
                SearchState.entity_types,
                entity_type_choice,
            ),
            custom_attrs={"data-testid": "entity-types"},
        ),
        style={"width": "100%"},
    )


def primary_source_choice(choice: tuple[str, SearchPrimarySource]) -> rx.Component:
    """Render a single checkbox for filtering by primary source."""
    return rx.checkbox(
        choice[1].title,
        checked=choice[1].checked,
        on_change=[
            SearchState.set_had_primary_source(choice[0]),
            SearchState.go_to_first_page,
            SearchState.push_search_params,
            SearchState.refresh,
            SearchState.resolve_identifiers,
        ],
    )


def primary_source_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by primary source."""
    return rx.card(
        rx.text("hadPrimarySource", margin_bottom="0.5em"),
        rx.vstack(
            rx.foreach(
                SearchState.had_primary_sources,
                primary_source_choice,
            ),
            custom_attrs={"data-testid": "had-primary-sources"},
        ),
        style={"width": "100%"},
    )


def sidebar() -> rx.Component:
    """Render sidebar with a search input and checkboxes for filtering entity types."""
    return rx.vstack(
        search_input(),
        entity_type_filter(),
        primary_source_filter(),
        spacing="4",
        custom_attrs={"data-testid": "search-sidebar"},
        style={"width": "25%"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous"),
            on_click=[
                SearchState.go_to_previous_page,
                SearchState.push_search_params,
                SearchState.scroll_to_top,
                SearchState.refresh,
                SearchState.resolve_identifiers,
            ],
            disabled=SearchState.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style={"minWidth": "10%"},
        ),
        rx.select(
            SearchState.total_pages,
            value=cast("rx.vars.NumberVar", SearchState.current_page).to_string(),
            on_change=[
                SearchState.set_page,
                SearchState.push_search_params,
                SearchState.scroll_to_top,
                SearchState.refresh,
                SearchState.resolve_identifiers,
            ],
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next"),
            on_click=[
                SearchState.go_to_next_page,
                SearchState.push_search_params,
                SearchState.scroll_to_top,
                SearchState.refresh,
                SearchState.resolve_identifiers,
            ],
            disabled=SearchState.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style={"minWidth": "10%"},
        ),
        spacing="4",
        style={"width": "100%"},
    )


def results_summary() -> rx.Component:
    """Render a summary of the results found."""
    return rx.center(
        rx.text(
            f"Showing {SearchState.current_results_length} "
            f"of {SearchState.total} items",
            style={
                "color": "var(--gray-12)",
                "fontWeight": "var(--font-weight-bold)",
                "margin": "var(--space-4)",
                "userSelect": "none",
            },
            custom_attrs={"data-testid": "search-results-summary"},
        ),
        style={"width": "100%"},
    )


def search_results() -> rx.Component:
    """Render the search results with a summary, result list, and pagination."""
    return rx.vstack(
        results_summary(),
        rx.foreach(
            SearchState.results,
            search_result,
        ),
        pagination(),
        spacing="4",
        custom_attrs={"data-testid": "search-results-section"},
        style={
            "minWidth": "0",
            "width": "100%",
        },
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.hstack(
            sidebar(),
            search_results(),
            spacing="4",
            style={"width": "100%"},
        )
    )
