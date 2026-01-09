from typing import Any

import reflex as rx

from mex.editor.components import (
    pagination,
)
from mex.editor.ingest.models import AuxProvider, IngestResult
from mex.editor.ingest.state import IngestState
from mex.editor.layout import page
from mex.editor.search_result_component import (
    SearchResultListItemOptions,
    SearchResultListOptions,
    search_result_list,
)


def ingest_button(result: IngestResult, index: int) -> rx.Component:
    """Render a button to ingest the ingest result to the MEx backend."""
    return rx.cond(
        result.show_ingest_button,
        rx.button(
            IngestState.label_button_ingest,
            align="end",
            color_scheme="jade",
            variant="surface",
            on_click=IngestState.ingest_result(index),  # type: ignore[misc]
            width="calc(8em * var(--scaling))",
            custom_attrs={"data-testid": f"ingest-button-{index}"},
        ),
        rx.button(
            IngestState.label_button_ingested,
            align="end",
            color_scheme="gray",
            variant="surface",
            disabled=True,
            width="calc(8em * var(--scaling))",
            custom_attrs={"data-testid": f"ingest-button-{index}"},
        ),
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
                    placeholder=IngestState.label_search_placeholder,
                    style=rx.Style(
                        {
                            "--text-field-selection-color": "",
                            "--text-field-focus-color": "transparent",
                            "--text-field-border-width": "1px",
                            "backgroundClip": "content-box",
                            "backgroundColor": "transparent",
                            "boxShadow": (
                                "inset 0 0 0 var(--text-field-border-width) transparent"
                            ),
                            "color": "",
                        }
                    ),
                    disabled=IngestState.is_loading,
                    type="text",
                    custom_attrs={"data-testid": "search-input"},
                ),
                rx.button(
                    rx.icon("search"),
                    type="submit",
                    variant="surface",
                    disabled=IngestState.is_loading,
                    custom_attrs={"data-testid": "search-button"},
                ),
                width="100%",
            ),
            on_submit=[
                IngestState.handle_submit,
                IngestState.go_to_first_page,
                IngestState.refresh,
                IngestState.resolve_identifiers,
                IngestState.flag_ingested_items,
            ],
            style=rx.Style(margin="1em 0"),
            justify="center",
            align="center",
        )
    )


def results_summary() -> rx.Component:
    """Render a summary of the results found."""
    return rx.center(
        rx.text(
            IngestState.label_search_result_summary_format,
            style=rx.Style(
                color="var(--gray-12)",
                fontWeight="var(--font-weight-bold)",
                margin="var(--space-4)",
                userSelect="none",
            ),
            custom_attrs={"data-testid": "search-results-summary"},
        ),
        style=rx.Style(width="100%"),
    )


def search_results() -> rx.Component:
    """Render the search results with a heading, result list, and pagination."""
    return rx.cond(
        IngestState.is_loading,
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(
                marginTop="var(--space-6)",
                width="100%",
            ),
        ),
        rx.vstack(
            results_summary(),
            search_result_list(
                IngestState.results_transformed,  # type: ignore[arg-type]
                SearchResultListOptions(
                    item_options=SearchResultListItemOptions(
                        render_append_fn=ingest_button  # type: ignore[arg-type]
                    )
                ),
            ),
            # rx.foreach(
            #     IngestState.results_transformed,
            #     ingest_result,
            # ),
            rx.center(
                pagination(IngestState, IngestState.flag_ingested_items),
            ),
            spacing="4",
            custom_attrs={"data-testid": "search-results-section"},
            align="stretch",
            style=rx.Style(
                minWidth="0",
                width="100%",
            ),
        ),
    )


def search_infobox() -> rx.Component | rx.Var[Any]:
    """Render information about the specific search provider query format."""
    return rx.match(
        IngestState.current_aux_provider,
        (
            AuxProvider.LDAP,
            rx.callout(IngestState.label_search_info_ldap),
        ),
        (
            AuxProvider.WIKIDATA,
            rx.callout(IngestState.label_search_info_wikidata),
        ),
    )


def tab_list() -> rx.Component:
    """Render the list of aux providers as a tab navigation."""
    return rx.center(
        rx.tabs.list(
            rx.spacer(),
            rx.foreach(
                IngestState.aux_providers,
                lambda provider: rx.tabs.trigger(
                    provider,
                    value=provider,
                    disabled=IngestState.is_loading,
                ),
            ),
            rx.spacer(),
            style=rx.Style(width="calc(24em * var(--scaling))"),
        )
    )


def tab_content() -> rx.Component:
    """Render the tab content with search components for each aux provider."""
    return rx.foreach(
        IngestState.aux_providers,
        lambda provider: rx.tabs.content(
            rx.vstack(
                search_input(),
                search_infobox(),
                search_results(),
                justify="center",
                align="center",
                spacing="5",
            ),
            value=provider,
        ),
    )


def index() -> rx.Component:
    """Return the index for the search component."""
    return page(
        rx.tabs.root(
            tab_list(),
            rx.spacer(),
            tab_content(),
            default_value=f"{IngestState.current_aux_provider}",
            on_change=[
                IngestState.set_current_aux_provider,
                IngestState.reset_query_string,
                IngestState.go_to_first_page,
                IngestState.refresh,
                IngestState.resolve_identifiers,
                IngestState.flag_ingested_items,
            ],
            custom_attrs={"data-testid": "aux-tab-section"},
            style=rx.Style(
                width="100%",
                padding="0 calc(var(--space-8) * var(--scaling))",
            ),
        )
    )
