import reflex as rx

from mex.editor.aux_extractor.state import AuxState
from mex.editor.layout import page


def search_input() -> rx.Component:
    """Render a search input element that will trigger the results to refresh."""
    return rx.debounce_input(
        rx.input(
            rx.input.slot(rx.icon("search"), padding_left="0"),
            placeholder="Search here...",
            value=AuxState.query_string,
            on_change=AuxState.set_query_string,
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


def search_bar() -> rx.Component:
    """Render a bar with an extractor menu."""
    return rx.center(
        rx.flex(
            rx.foreach(
                AuxState.aux_items,
                lambda item: rx.text(
                    item,
                    cursor="pointer",
                ),
            ),
            direction="row",
            gap="10px",
        ),
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous", weight="bold"),
            on_click=None,
            spacing="2",
            width="120px",
            margin_right="10px",
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
        ),
        rx.select(
            AuxState.total_pages,
            value=AuxState.current_page.to_string(),  # type: ignore[attr-defined]
            on_change=AuxState.set_page,
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next", weight="bold"),
            on_click=None,
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
                f"showing {AuxState.current_results_length} "
                f"of total {AuxState.total} items found",
                custom_attrs={"data-testid": "search-results-heading"},
                size="3",
            ),
            style={"margin": "1em 0"},
            width="100%",
        ),
        pagination(),
        custom_attrs={"data-testid": "search-results-section"},
        width="70vw",
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.vstack(
            search_bar(),
            search_input(),
            search_results(),
            spacing="5",
        ),
    )
