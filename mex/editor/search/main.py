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
            style={"margin": "1em 0 1em"},
            debounce_timeout=250,
        )
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
        style={"margin": "2em 0"},
    )


def sidebar() -> rx.Component:
    """Render sidebar with a search input and checkboxes for filtering entity types."""
    return rx.box(
        search_input(),
        entity_type_filter(),
        style={
            "width": "20vw",
            "padding": "2em 2em 10em",
        },
        custom_attrs={"data-testid": "search-sidebar"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous", weight="bold"),
            on_click=SearchState.go_to_previous_page,
            disabled=SearchState.disable_previous_page,
            spacing="2",
            width="120px",
            margin_right="10px",
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
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
            spacing="2",
            width="120px",
            margin_left="10px",
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
        ),
        style={"margin": "1em 0"},
        width="100%",
    )


def search_results() -> rx.Component:
    """Render the search results with a summary, result list, and pagination."""
    return rx.vstack(
        rx.center(
            rx.text(
                f"Showing {SearchState.current_results_length} "
                f"of {SearchState.total} items",
                style={"color": "var(--gray-12)", "userSelect": "none"},
                weight="bold",
                custom_attrs={"data-testid": "search-results-summary"},
            ),
            style={"margin": "2em 0 1em"},
            width="100%",
        ),
        rx.foreach(
            SearchState.results,
            search_result,
        ),
        pagination(),
        custom_attrs={"data-testid": "search-results-section"},
        width="100%",
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        sidebar(),
        search_results(),
    )
