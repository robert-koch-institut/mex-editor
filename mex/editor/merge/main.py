from typing import Literal

import reflex as rx

from mex.editor.components import render_value
from mex.editor.layout import page
from mex.editor.merge.state import MergeState
from mex.editor.search.models import SearchResult


def search_result(
    result: SearchResult,
    index: int,
    category: Literal["merged", "extracted"],
) -> rx.Component:
    """Render a single merged or extracted item search result with checkbox."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.checkbox(
                    checked=MergeState.selected_items[category] == index,
                    on_change=MergeState.select_item(category, index),
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
        custom_attrs={"data-testid": f"result-{category}-{index}"},
    )


def results_summary(category: Literal["merged", "extracted"]) -> rx.Component:
    """Render a summary of the results found."""
    return rx.center(
        rx.text(
            f"Showing {MergeState.results_count[category]} "
            f"of {MergeState.total_count[category]} items",
            style={
                "color": "var(--gray-12)",
                "fontWeight": "var(--font-weight-bold)",
                "margin": "var(--space-4)",
                "userSelect": "none",
            },
        ),
        style={"width": "100%"},
        custom_attrs={"data-testid": f"{category}-results-summary"},
    )


def entity_type_choice_merged(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by merged entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=[
            MergeState.set_entity_type_merged(choice[0]),
            MergeState.refresh(["merged"]),
            MergeState.resolve_identifiers,
        ],
        disabled=MergeState.is_loading,
    )


def entity_type_choice_extracted(choice: tuple[str, bool]) -> rx.Component:
    """Render a single checkbox for filtering by extracted entity type."""
    return rx.checkbox(
        choice[0],
        checked=choice[1],
        on_change=[
            MergeState.set_entity_type_extracted(choice[0]),
            MergeState.refresh(["extracted"]),
            MergeState.resolve_identifiers,
        ],
        disabled=MergeState.is_loading,
    )


def entity_type_filter(category: Literal["merged", "extracted"]) -> rx.Component:
    """Render checkboxes for filtering the search results by entity type."""
    return rx.card(
        rx.text("Filter by Entity Type", margin_bottom="0.5em", size="1"),
        rx.scroll_area(
            rx.flex(
                rx.cond(
                    category == "merged",
                    rx.vstack(
                        rx.foreach(
                            MergeState.entity_types_merged,
                            entity_type_choice_merged,
                        ),
                        custom_attrs={"data-testid": "entity-types-merged"},
                    ),
                    rx.vstack(
                        rx.foreach(
                            MergeState.entity_types_extracted,
                            entity_type_choice_extracted,
                        ),
                        custom_attrs={"data-testid": "entity-types-extracted"},
                    ),
                ),
            ),
            type="always",
            scrollbars="vertical",
            style={"height": 90},
        ),
    )


def search_input(category: Literal["merged", "extracted"]) -> rx.Component:
    """Render a search input and buttons for the results to refresh."""
    return rx.vstack(
        rx.form.root(
            rx.card(
                rx.input(
                    autofocus=True,
                    default_value=MergeState.query_strings[category],
                    value=MergeState.query_strings[category],
                    max_length=100,
                    name=f"query_string_{category}",
                    on_change=MergeState.handle_submit(category),
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
                    custom_attrs={"data-testid": f"search-input-{category}"},
                ),
            ),
            rx.spacer(height="var(--space-2)"),
            entity_type_filter(category),
            rx.hstack(
                rx.button(
                    "Clear",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=MergeState.clear_input(category),
                    custom_attrs={"data-testid": f"clear-button-{category}"},
                ),
                rx.button(
                    rx.icon("Search"),
                    type="submit",
                    variant="surface",
                    disabled=MergeState.is_loading,
                    on_click=[
                        MergeState.refresh([category]),
                        MergeState.resolve_identifiers,
                    ],
                    custom_attrs={"data-testid": f"search-button-{category}"},
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
    """Render a submit button to commit the merging."""
    return rx.button(
        "Submit Merge",
        color_scheme="jade",
        size="3",
        on_click=MergeState.submit_merge_items,
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def search_panel(category: Literal["merged", "extracted"]) -> rx.Component:
    """Return the search interface."""
    return rx.vstack(
        rx.heading(
            f"Search {category} items",
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "width": "100%",
            },
            custom_attrs={"data-testid": f"create-heading-{category}"},
        ),
        search_input(category),
        results_summary(category),
        rx.cond(
            category == "merged",
            rx.foreach(
                MergeState.results_merged,
                lambda result, index: search_result(result, index, category="merged"),
            ),
            rx.foreach(
                MergeState.results_extracted,
                lambda result, index: search_result(
                    result, index, category="extracted"
                ),
            ),
        ),
        style={"width": "50%", "margin": "var(--space-4)", "align": "center"},
    )


def index() -> rx.Component:
    """Return the index for the merge and extracted search component."""
    return page(
        rx.vstack(
            rx.hstack(
                search_panel(category="merged"),
                search_panel(category="extracted"),
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
