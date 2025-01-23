import reflex as rx

from mex.editor.aux_search.models import AuxResult
from mex.editor.aux_search.state import AuxState
from mex.editor.components import render_value
from mex.editor.layout import page


def expand_properties_button(result: AuxResult) -> rx.Component:
    """Render a button to expand all properties of a aux search result."""
    return rx.button(
        rx.cond(
            result.show_properties,
            rx.icon("minimize-2", size=15),
            rx.icon("maximize-2", size=15),
        ),
        on_click=AuxState.toggle_show_properties(result),  # type: ignore [call-arg,func-returns-value]
        align="end",
        custom_attrs={"data-testid": "expand-properties-button"},
    )


def render_preview(result: AuxResult) -> rx.Component:
    """Render a preview of the aux search result."""
    return rx.text(
        rx.hstack(
            rx.foreach(
                result.preview,
                render_value,
            )
        ),
        weight="light",
        style={
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": "80%",
        },
    )


def render_all_properties(result: AuxResult) -> rx.Component:
    """Render all properties of the aux search result."""
    return rx.text(
        rx.hstack(
            rx.foreach(
                result.all_properties,
                render_value,  # write custom function!!
            )
        ),
        weight="light",
        style={
            "whiteSpace": "nowrap",
            "maxWidth": "80%",
        },
        custom_attrs={"data-testid": "all-properties-display"},
    )


def aux_search_result(result: AuxResult) -> rx.Component:
    """Render a single aux search result."""
    return rx.box(
        rx.card(
            rx.hstack(
                rx.text(
                    rx.hstack(
                        rx.foreach(
                            result.title,
                            render_value,
                        )
                    ),
                    weight="bold",
                    style={
                        "whiteSpace": "nowrap",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "maxWidth": "100%",
                    },
                ),
                expand_properties_button(result),
            ),
            rx.cond(
                result.show_properties,
                render_all_properties(result),
                render_preview(result),
            ),
            style={"width": "100%"},
        ),
        style={"width": "100%"},
    )


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
        width="100%",
    )


def nav_bar() -> rx.Component:
    """Render a bar with an extractor navigation menu."""
    return rx.flex(
        rx.foreach(
            AuxState.aux_data_sources,
            lambda item: rx.text(
                item,
                cursor="pointer",
                size="5",
            ),
        ),
        direction="row",
        gap="50px",
        custom_attrs={"data-testid": "aux-nav-bar"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous", weight="bold"),
            on_click=AuxState.go_to_previous_page,
            disabled=AuxState.disable_previous_page,
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
            on_click=AuxState.go_to_next_page,
            disabled=AuxState.disable_next_page,
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
        rx.foreach(
            AuxState.results,
            aux_search_result,
        ),
        pagination(),
        custom_attrs={"data-testid": "search-results-section"},
        width="70vw",
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return rx.center(
        page(
            rx.vstack(
                nav_bar(),
                search_input(),
                search_results(),
                spacing="5",
                justify="center",
                align="center",
                padding="30px",
            ),
        ),
        width="100%",
    )
