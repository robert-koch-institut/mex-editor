from typing import cast

import reflex as rx

from mex.editor.aux_search.models import AuxNavItem, AuxResult
from mex.editor.aux_search.state import AuxState
from mex.editor.components import render_value
from mex.editor.layout import page


def expand_properties_button(result: AuxResult, index: int) -> rx.Component:
    """Render a button to expand all properties of an aux search result."""
    return rx.button(
        rx.cond(
            result.show_properties,
            rx.icon("minimize-2", size=15),
            rx.icon("maximize-2", size=15),
        ),
        on_click=lambda: AuxState.toggle_show_properties(index),
        align="end",
        custom_attrs={"data-testid": "expand-properties-button"},
    )


def import_button(result: AuxResult, index: int) -> rx.Component:
    """Render a button to import the aux search result to the MEx backend."""
    return rx.cond(
        result.show_import_button,
        rx.button(
            "Import",
            on_click=AuxState.import_result(index),
            align="end",
        ),
        rx.button(
            "Imported",
            align="end",
            disabled=True,
        ),
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
        style={
            "fontWeight": "var(--font-weight-light)",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": "100%",
        },
    )


def render_all_properties(result: AuxResult) -> rx.Component:
    """Render all properties of the aux search result."""
    return rx.text(
        rx.hstack(
            rx.foreach(
                result.all_properties,
                render_value,
            ),
            style={
                "fontWeight": "var(--font-weight-light)",
                "flexWrap": "wrap",
                "alignItems": "start",
            },
        ),
        custom_attrs={"data-testid": "all-properties-display"},
    )


def result_title_and_buttons(result: AuxResult, index: int) -> rx.Component:
    """Render the title and buttons for an aux search result."""
    return rx.hstack(
        rx.text(
            rx.hstack(
                rx.foreach(
                    result.title,
                    render_value,
                )
            ),
            style={
                "fontWeight": "var(--font-weight-bold)",
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "95%",
            },
        ),
        expand_properties_button(result, index),
        import_button(result, index),
        style={"width": "100%"},
    )


def aux_search_result(result: AuxResult, index: int) -> rx.Component:
    """Render an aux search result with title, buttons and preview or all properties."""
    return rx.box(
        rx.card(
            rx.vstack(
                result_title_and_buttons(result, index),
                rx.cond(
                    result.show_properties,
                    render_all_properties(result),
                    render_preview(result),
                ),
            ),
            style={
                "width": "100%",
                "flexWrap": "wrap",
            },
        ),
        style={"width": "100%"},
    )


def search_input() -> rx.Component:
    """Render a search input element that will trigger the results to refresh."""
    return rx.center(
        rx.form(
            rx.hstack(
                rx.input(
                    autofocus=True,
                    max_length=100,
                    name="query_string",
                    placeholder="Search here...",
                    style={
                        "--text-field-selection-color": "",
                        "--text-field-focus-color": "transparent",
                        "--text-field-border-width": "1px",
                        "backgroundClip": "content-box",
                        "backgroundColor": "transparent",
                        "boxShadow": (
                            "inset 0 0 0 var(--text-field-border-width) transparent"
                        ),
                        "color": "",
                    },
                    type="text",
                ),
                rx.button(rx.icon("search"), type="submit"),
                width="100%",
            ),
            on_submit=AuxState.handle_submit,
            style={"margin": "1em 0 1em"},
            justify="center",
            align="center",
        )
    )


def search_results() -> rx.Component:
    """Render the search results with a heading, result list, and pagination."""
    return rx.vstack(
        rx.center(
            rx.text(
                f"Showing {AuxState.current_results_length} "
                f"of {AuxState.total} items found",
                style={
                    "color": "var(--gray-12)",
                    "fontWeight": "var(--font-weight-bold)",
                    "margin": "var(--space-4)",
                    "userSelect": "none",
                },
                custom_attrs={"data-testid": "search-results-heading"},
            ),
            style={"width": "100%"},
        ),
        rx.foreach(
            AuxState.results_transformed,
            aux_search_result,
        ),
        pagination(),
        custom_attrs={"data-testid": "search-results-section"},
        width="70vw",
    )


def aux_provider_tab(item: AuxNavItem) -> rx.Component:
    """Render a tab for an aux provider."""
    return rx.tabs.trigger(
        item.title,
        value=item.value,
    )


def nav_bar() -> rx.Component:
    """Render a bar with an extractor navigation menu."""
    return rx.flex(
        rx.tabs.root(
            rx.tabs.list(
                rx.spacer(),
                rx.foreach(
                    AuxState.aux_provider_items,
                    lambda item: aux_provider_tab(item),
                ),
                rx.spacer(),
                size="2",
            ),
            rx.spacer(),
            rx.tabs.content(
                rx.vstack(
                    search_input(),
                    search_results(),
                    justify="center",
                    align="center",
                    spacing="5",
                ),
                value="wikidata",
            ),
            rx.tabs.content(
                rx.vstack(
                    search_input(),
                    search_results(),
                    justify="center",
                    align="center",
                    spacing="5",
                ),
                value="ldap",
            ),
            rx.tabs.content(
                rx.vstack(
                    search_input(),
                    search_results(),
                    justify="center",
                    align="center",
                    spacing="5",
                ),
                value="orcid",
            ),
            default_value="wikidata",
            on_change=lambda value: AuxState.change_extractor(value),
        ),
        custom_attrs={"data-testid": "aux-nav-bar"},
    )


def pagination() -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous"),
            on_click=AuxState.go_to_previous_page,
            disabled=AuxState.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style={"minWidth": "10%"},
        ),
        rx.select(
            AuxState.total_pages,
            value=cast("rx.vars.NumberVar", AuxState.current_page).to_string(),
            on_change=AuxState.set_page,
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next", weight="bold"),
            on_click=AuxState.go_to_next_page,
            disabled=AuxState.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style={"minWidth": "10%"},
        ),
        spacing="4",
        style={"width": "100%"},
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return rx.center(
        page(
            nav_bar(),
        )
    )
