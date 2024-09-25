import reflex as rx
import reflex_chakra as rc

from mex.editor.layout import page
from mex.editor.search.models import SearchResult
from mex.editor.search.state import SearchState


def search_result(result: SearchResult) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(
        rx.link(
            rx.text(
                result.title,
                weight="bold",
                style={
                    "whiteSpace": "nowrap",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "maxWidth": "100%",
                },
            ),
            rx.text(
                result.preview,
                weight="light",
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
                    on_change=lambda val: SearchState.set_entity_type(val, choice[0]),  # type: ignore[call-arg]
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
        width="20%",
        height="100vh",
        padding="20px",
        style={"margin": "2em 0 0 -1em"},
        bg=rx.color("gray", 2),
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
            value=f"{SearchState.current_page}",
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
    )


def main_content() -> rx.Component:
    """Render the search results with a heading, result list, and pagination."""
    return rx.section(
        rx.center(
            rx.heading(
                f"showing {SearchState.current_results_length} "
                f"of total {SearchState.total} items found",
                custom_attrs={"data-testid": "search-results-heading"},
                style={"margin": "1em 0"},
                size="3",
            ),
        ),
        rx.vstack(
            rx.foreach(
                SearchState.results,
                search_result,
            ),
        ),
        pagination(),
        on_mount=SearchState.refresh,
        style={"width": "70%", "margin": "2em 0 0 1em"},
        custom_attrs={"data-testid": "search-results-section"},
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        sidebar(),
        main_content(),
    )
