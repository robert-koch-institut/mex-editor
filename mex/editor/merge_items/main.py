import reflex as rx

from mex.editor.components import render_value
from mex.editor.layout import page
from mex.editor.merge_items.state import MergeState
from mex.editor.search.models import SearchResult


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


def entity_type_choice(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=[
            MergeState.set_entity_type(choice[0]),
            # MergeState.push_search_params,
            MergeState.refresh,
            # MergeState.resolve_identifiers,
        ],
        disabled=MergeState.is_loading,
    )


def entity_type_filter() -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.card(
        rx.text("Filter by Entity Type", margin_bottom="0.5em", size="1"),
        rx.scroll_area(
            rx.flex(
                rx.vstack(
                    rx.foreach(
                        MergeState.entity_types,
                        entity_type_choice,
                    ),
                    custom_attrs={"data-testid": "entity-types"},
                ),
            ),
            type="always",
            scrollbars="vertical",
            style={"height": 90},
        ),
    )


def search_input() -> rx.Component:
    """Render a search input element that will trigger the results to refresh."""
    return rx.vstack(
        rx.form.root(
            rx.card(
                rx.input(
                    autofocus=True,
                    default_value=MergeState.query_string,
                    max_length=100,
                    name="query_string",
                    placeholder="Search here...",
                    style={
                        "--text-field-selection-color": "",
                        "--text-field-focus-color": "transparent",
                        "--text-field-border-width": "calc(1px * var(--scaling))",
                        "boxShadow": (
                            "inset 0 0 0 var(--text-field-border-width) transparent"
                        ),
                    },
                    tab_index=1,
                    type="text",
                ),
            ),
            entity_type_filter(),
            rx.button(
                "Clear",
                variant="surface",
                disabled=MergeState.is_loading,
                custom_attrs={"data-testid": "clear-button"},
            ),
            rx.spacer(),
            rx.button(
                rx.icon("Search"),
                type="submit",
                variant="surface",
                disabled=MergeState.is_loading,
                custom_attrs={"data-testid": "search-button"},
            ),
            on_submit=[
                # MergeState.handle_submit,
                # MergeState.push_search_params,
                MergeState.refresh,
                # MergeState.resolve_identifiers,
            ],
        ),
        spacing="4",
        style={"width": "100%"},
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        "Submit Merge",
        color_scheme="jade",
        size="3",
        on_click=MergeState.submit_merge_items,
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def extracted_search() -> rx.Component:
    """Return the heading for the create page."""
    return rx.vstack(
        rx.heading(
            "Search extracted items",
            custom_attrs={"data-testid": "create-heading"},
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "100%",
            },
        ),
        search_input(),
        rx.foreach(
            MergeState.results_extracted,
            search_result,
        ),
        style={"width": "100%"},
    )


def merged_search() -> rx.Component:
    """Return the heading for the create page."""
    return rx.vstack(
        rx.heading(
            "Search merged items",
            custom_attrs={"data-testid": "create-heading"},
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "100%",
            },
        ),
        search_input(),
        rx.foreach(
            MergeState.results_merged,
            search_result,
        ),
        style={"width": "100%"},
    )


def index() -> rx.Component:
    """Return the index for the merge component."""
    return page(
        rx.vstack(
            rx.hstack(
                merged_search(),
                extracted_search(),
                spacing="4",
                style={"width": "100%"},
            ),
            submit_button(),
        ),
    )
