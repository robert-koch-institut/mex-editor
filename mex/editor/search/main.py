from typing import cast

import reflex as rx
import reflex_chakra as rc

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
    return rx.debounce_input(
        rx.input(
            rx.input.slot(rx.icon("search"), padding_left="0"),
            placeholder="Search here...",
            value=SearchState.query_string,
            on_change=SearchState.set_query_string,
            max_length=100,
            style={
                "--text-field-selection-color": "",
                "--text-field-focus-color": "transparent",
                "--text-field-border-width": "1px",
                "backgroundClip": "content-box",
                "backgroundColor": "transparent",
                "boxShadow": ("inset 0 0 0 var(--text-field-border-width) transparent"),
                "color": "",
            },
        ),
        style={"margin": "1em 0 1em"},
        debounce_timeout=250,
    )


def entity_type_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.vstack(
        rx.foreach(
            SearchState.entity_types,
            lambda choice: rx.debounce_input(
                rc.checkbox(
                    choice[0],
                    checked=choice[1],
                    on_change=lambda val: cast(
                        SearchState, SearchState
                    ).set_entity_type(
                        val,
                        choice[0],
                    ),
                ),
                debounce_timeout=100,
            ),
        ),
        custom_attrs={"data-testid": "entity-types"},
        style={"margin": "2em 0"},
    )


def sidebar() -> rx.Component:
    """Render sidebar with a search input and checkboxes for filtering entity types."""
    return rx.box(
        search_input(),
        entity_type_filter(),
        width="20vw",
        padding="2em 2em 10em",
        bg="linear-gradient(to bottom, var(--gray-2) 0%, var(--color-background) 100%)",
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
            rx.text("Next", weight="bold"),
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
    """Render the search results with a heading, result list, and pagination."""
    return rx.vstack(
        rx.center(
            rx.heading(
                f"showing {SearchState.current_results_length} "
                f"of total {SearchState.total} items found",
                custom_attrs={"data-testid": "search-results-heading"},
                size="3",
            ),
            style={"margin": "1em 0"},
            width="100%",
        ),
        rx.foreach(
            SearchState.results,
            search_result,
        ),
        pagination(),
        custom_attrs={"data-testid": "search-results-section"},
        width="70vw",
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        sidebar(),
        search_results(),
    )
