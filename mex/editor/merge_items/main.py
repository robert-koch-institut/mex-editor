import reflex as rx

from mex.editor.components import render_value
from mex.editor.layout import page
from mex.editor.merge_items.state import MergeState
from mex.editor.search.models import SearchResult


def merged_search_result(result: SearchResult, index: int) -> rx.Component:
    """Render a single merged item search result."""
    return rx.card(
        rx.hstack(
            rx.checkbox(
                checked=MergeState.selected_merged == index,
                on_change=MergeState.select_merged_item(index),
            ),
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
        ),
        style={"width": "100%"},
        class_name="search-result-card",
        custom_attrs={"data-testid": f"result-merged-{index}"},
    )


def extracted_search_result(result: SearchResult, index: int) -> rx.Component:
    """Render a single extracted item search result."""
    return rx.card(
        rx.hstack(
            rx.checkbox(
                checked=MergeState.selected_extracted == index,
                on_change=MergeState.select_extracted_item(index),
            ),
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
        ),
        style={"width": "100%"},
        class_name="search-result-card",
        custom_attrs={"data-testid": f"result-extracted-{index}"},
    )


def merged_results_summary() -> rx.Component:
    """Render a summary of the merged results found."""
    return rx.center(
        rx.text(
            f"Showing {MergeState.current_merged_results_length} "
            f"of {MergeState.total_merged} items",
            style={
                "color": "var(--gray-12)",
                "fontWeight": "var(--font-weight-bold)",
                "margin": "var(--space-4)",
                "userSelect": "none",
            },
        ),
        style={"width": "100%"},
    )


def extracted_results_summary() -> rx.Component:
    """Render a summary of the extracted results found."""
    return rx.center(
        rx.text(
            f"Showing {MergeState.current_extracted_results_length} "
            f"of {MergeState.total_extracted} items",
            style={
                "color": "var(--gray-12)",
                "fontWeight": "var(--font-weight-bold)",
                "margin": "var(--space-4)",
                "userSelect": "none",
            },
        ),
        style={"width": "100%"},
    )


def entity_type_choice_merged(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by merged entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=MergeState.set_entity_type_merged(choice[0]),
        disabled=MergeState.is_loading,
    )


def entity_type_choice_extracted(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by extracted entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=MergeState.set_entity_type_extracted(choice[0]),
        disabled=MergeState.is_loading,
    )


def entity_type_filter_merged() -> rx.Component:
    """Render checkboxes for filtering the merged search results by entity type."""
    return rx.card(
        rx.text("Filter by Entity Type", margin_bottom="0.5em", size="1"),
        rx.scroll_area(
            rx.flex(
                rx.vstack(
                    rx.foreach(
                        MergeState.entity_types_merged,
                        entity_type_choice_merged,
                    ),
                    custom_attrs={"data-testid": "entity-types-merged"},
                ),
            ),
            type="always",
            scrollbars="vertical",
            style={"height": 90},
        ),
    )


def entity_type_filter_extracted() -> rx.Component:
    """Render checkboxes for filtering the extracted search results by entity type."""
    return rx.card(
        rx.text("Filter by Entity Type", margin_bottom="0.5em", size="1"),
        rx.scroll_area(
            rx.flex(
                rx.vstack(
                    rx.foreach(
                        MergeState.entity_types_extracted,
                        entity_type_choice_extracted,
                    ),
                    custom_attrs={"data-testid": "entity-types-extracted"},
                ),
            ),
            type="always",
            scrollbars="vertical",
            style={"height": 90},
        ),
    )


def search_input_merged() -> rx.Component:
    """Render a merged search input that will trigger the results to refresh."""
    return rx.vstack(
        rx.form.root(
            rx.card(
                rx.input(
                    autofocus=True,
                    default_value=MergeState.query_string_merged,
                    value=MergeState.query_string_merged,
                    max_length=100,
                    name="query_string_merged",
                    on_change=MergeState.handle_submit_merged,
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
                    custom_attrs={"data-testid": "search-input-merged"},
                ),
            ),
            rx.spacer(height="var(--space-2)"),
            entity_type_filter_merged(),
            rx.hstack(
                rx.button(
                    "Clear",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=MergeState.clear_input_merged,
                    custom_attrs={"data-testid": "clear-button-merged"},
                ),
                rx.button(
                    rx.icon("Search"),
                    type="submit",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=MergeState.refresh_merged,
                    custom_attrs={"data-testid": "search-button-merged"},
                ),
                justify="center",
                align="center",
                spacing="2",
                margin="var(--space-4)",
            ),
        ),
        style={"width": "100%", "margin-bottom": "var(--space-4)"},
    )


def search_input_extracted() -> rx.Component:
    """Render a extracted search input that will trigger the results to refresh."""
    return rx.vstack(
        rx.form.root(
            rx.card(
                rx.input(
                    autofocus=True,
                    default_value=MergeState.query_string_extracted,
                    value=MergeState.query_string_extracted,
                    max_length=100,
                    name="query_string_extracted",
                    placeholder="Search here...",
                    on_change=MergeState.handle_submit_extracted,
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
                    custom_attrs={"data-testid": "search-input-extracted"},
                ),
            ),
            rx.spacer(height="var(--space-2)"),
            entity_type_filter_extracted(),
            rx.hstack(
                rx.button(
                    "Clear",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=MergeState.clear_input_extracted,
                    custom_attrs={"data-testid": "clear-button-extracted"},
                ),
                rx.button(
                    rx.icon("Search"),
                    type="submit",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=MergeState.refresh_extracted,
                    custom_attrs={"data-testid": "search-button-extracted"},
                ),
                justify="center",
                align="center",
                spacing="2",
                margin="var(--space-4)",
            ),
        ),
        style={"width": "100%", "margin-bottom": "var(--space-4)", "align": "center"},
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
    """Return the extracted search interface."""
    return rx.vstack(
        rx.heading(
            "Search extracted items",
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "100%",
            },
        ),
        search_input_extracted(),
        extracted_results_summary(),
        rx.foreach(
            MergeState.results_extracted,
            extracted_search_result,
        ),
        style={"width": "50%", "margin": "var(--space-4)", "align": "center"},
        custom_attrs={"data-testid": "search-extracted"},
    )


def merged_search() -> rx.Component:
    """Return the merged search interface."""
    return rx.vstack(
        rx.heading(
            "Search merged items",
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "100%",
            },
        ),
        search_input_merged(),
        merged_results_summary(),
        rx.foreach(
            MergeState.results_merged,
            merged_search_result,
        ),
        style={"width": "50%", "margin": "var(--space-4)", "align": "center"},
        custom_attrs={"data-testid": "search-merged"},
    )


def index() -> rx.Component:
    """Return the index for the merge and extracted search component."""
    return page(
        rx.vstack(
            rx.hstack(
                merged_search(),
                extracted_search(),
                style={"width": "100%", "align": "center", "justify": "center"},
            ),
            rx.box(
                submit_button(),
                style={
                    "justifyContent": "center",
                    "display": "flex",
                    "width": "100%",
                },
            ),
            style={
                "width": "100%",
                "align": "center",
                "justify": "center",
                "flex-grow": "1",
            },
        ),
    )
