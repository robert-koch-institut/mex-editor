from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.layout import page
from mex.editor.search.models import SearchResult
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
                style={"fontWeight": "bold"},
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
                    "fontWeight": "light",
                    "textDecoration": "none",
                },
            ),
            href=f"/item/{result.identifier}",
        ),
        style={"width": "100%"},
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
                on_change=SearchState.set_query_string,
                max_length=100,
                style={
                    "--text-field-selection-color": "",
                    "--text-field-focus-color": "transparent",
                    "--text-field-border-width": "1px",
                    "boxShadow": (
                        "inset 0 0 0 var(--text-field-border-width) transparent"
                    ),
                },
            ),
            style={"margin": "1rem 0 1rem"},
            debounce_timeout=250,
        ),
        style={"width": "100%"},
    )


def entity_type_choice(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkboxes for filtering by entity type."""
    return rx.checkbox(
        choice[0][len("Merged") :],
        checked=choice[1],
        on_change=SearchState.set_entity_type(choice[0]),
    )


def entity_type_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.card(
        rx.vstack(
            rx.foreach(
                SearchState.entity_types,
                entity_type_choice,
            ),
            custom_attrs={"data-testid": "entity-types"},
        ),
        style={"width": "100%"},
    )


def sidebar() -> rx.Component:
    """Render sidebar with a search input and checkboxes for filtering entity types."""
    return rx.vstack(
        search_input(),
        entity_type_filter(),
        spacing="4",
        custom_attrs={"data-testid": "search-sidebar"},
        style={"width": "25%"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous", weight="bold"),
            on_click=SearchState.go_to_previous_page,
            disabled=SearchState.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style={
                "width": "8rem",
                "margin": "0 2ch",
            },
        ),
        rx.select(
            SearchState.total_pages,
            value=cast(rx.vars.NumberVar, SearchState.current_page).to_string(),
            on_change=SearchState.set_page,
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next"),
            on_click=SearchState.go_to_next_page,
            disabled=SearchState.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style={
                "width": "8rem",
                "margin": "0 2ch",
            },
        ),
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
                "userSelect": "none",
                "fontWeight": "bold",
                "margin": "1rem",
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
        style={"width": "100%"},
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.hstack(
            sidebar(),
            search_results(),
            spacing="4",
            style={
                "margin": "0 2rem",
                "width": "100%",
            },
        )
    )
