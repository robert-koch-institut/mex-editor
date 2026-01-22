import reflex as rx

from mex.editor.advanced_search.state import AdvancedSearchState, RefFilter
from mex.editor.layout import page
from mex.editor.search_reference_dialog import search_reference_dialog
from mex.editor.value_label_select import value_label_select


def filter_query() -> rx.Component:
    """Render filter query page."""
    return rx.card(
        rx.form(
            rx.hstack(
                rx.input(
                    default_value=AdvancedSearchState.query,
                    max_length=100,
                    name="query",
                    placeholder=AdvancedSearchState.label_search_input_placeholder,
                    custom_attrs={"data-testid": "search-input"},
                ),
                rx.button(
                    rx.icon("search"),
                    type="submit",
                    variant="surface",
                    custom_attrs={"data-testid": "search-button"},
                ),
                align="stretch",
            ),
            on_submit=AdvancedSearchState.on_query_form_submit,
        )
    )


def filter_entity_type() -> rx.Component:
    """Render filter entity type page."""
    return rx.card(
        rx.vstack(
            rx.heading("Entity Types", size="3"),
            rx.vstack(
                rx.foreach(
                    AdvancedSearchState.all_entity_types,
                    lambda entity_type: rx.checkbox(
                        entity_type,
                        value=entity_type,
                        on_change=AdvancedSearchState.toggle_entity_type(entity_type),
                        default_checked=AdvancedSearchState.entity_types.contains(
                            entity_type
                        ),
                        custom_attrs={
                            "data-testid": f"entity-type-{entity_type}-checkbox"
                        },
                    ),
                ),
                align="stretch",
            ),
            align="stretch",
        )
    )


def ref_values_row(
    ref: RefFilter, index: int, val: str, val_index: int
) -> rx.Component:
    return rx.hstack(
        rx.input(
            value=val,
            placeholder=f"Identifier für '{ref.field_label}'",
            on_change=lambda value: AdvancedSearchState.set_ref_filter_value(
                index, val_index, value
            ),
            style=rx.Style(flex="1"),
        ),
        search_reference_dialog(
            field_label=ref.field_label,
            reference_types=ref.reference_value_type,
            on_identifier_selected=lambda value: AdvancedSearchState.set_ref_filter_value(
                index, val_index, value
            ),
        ),
        rx.icon_button(
            rx.icon(
                "minus",
                height="1rem",
                width="1rem",
            ),
            variant="soft",
            color_scheme="red",
            size="1",
            on_click=AdvancedSearchState.remove_ref_filter_value(index, val_index),
        ),
        align="center",
        style=rx.Style(padding_left="1em"),
    )


def ref_filter_row(ref: RefFilter, index: int) -> rx.Component:
    return rx.vstack(
        rx.vstack(
            value_label_select(
                items=AdvancedSearchState.all_fields_for_entity_types,
                value=ref.field,
                placeholder=AdvancedSearchState.label_reference_field_filter_placeholder,
                on_change=lambda value: AdvancedSearchState.set_ref_filter_field(
                    index, value
                ),
            ),
            rx.button(
                f"Remove {ref.field_label}",
                color_scheme="gray",
                variant="soft",
                size="1",
                class_name="truncate",
                style=rx.Style(align_self="end", max_width="60%", display="block"),
                on_click=AdvancedSearchState.remove_ref_filter(index),
                custom_attrs={"data-testid": f"ref-filter-{ref.field}-remove-button"},
            ),
            gap="4px",
            align="stretch",
        ),
        rx.foreach(
            ref["values"],
            lambda val, val_index: ref_values_row(ref, index, val, val_index),
        ),
        rx.button(
            f"Add {ref.field_label}",
            variant="ghost",
            color_scheme="jade",
            size="1",
            on_click=lambda: AdvancedSearchState.add_ref_filter_value(index, ""),
            class_name="truncate",
            style=rx.Style(
                align_self="end", margin_right="0", max_width="60%", display="block"
            ),
        ),
        align="stretch",
    )


def filter_references() -> rx.Component:
    """Render filter references page."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Reference Filters", size="3"),
                rx.button(
                    rx.icon("plus"),
                    on_click=AdvancedSearchState.add_ref_filter(
                        AdvancedSearchState.all_fields_for_entity_types[0].value
                    ),
                    variant="ghost",
                    color_scheme="jade",
                    style=rx.Style(margin_left="auto"),
                    custom_attrs={"data-testid": "add-reference-filter-button"},
                    size="1",
                ),
            ),
            rx.vstack(
                rx.foreach(
                    AdvancedSearchState.refs,
                    lambda ref, index: ref_filter_row(ref, index),
                ),
                align="stretch",
                spacing="4",
            ),
            align="stretch",
        )
    )


def sidebar() -> rx.Component:
    """Render sidebar with filters for the search page."""
    return rx.vstack(
        filter_query(), filter_entity_type(), filter_references(), align="stretch"
    )


def search_results() -> rx.Component:
    """Render search results page."""
    return rx.box(
        rx.text("Search Results"),
        rx.text(f"Query: {AdvancedSearchState.query}"),
        rx.text(f"Entity Types: {AdvancedSearchState.entity_types}"),
        rx.text("Refs: "),
        rx.vstack(
            rx.foreach(
                AdvancedSearchState.refs,
                lambda ref: rx.text(f"Field: {ref.field}, Values: {ref.values}"),
            )
        ),
        style=rx.Style(flex="1", padding="1rem"),
    )


def index() -> rx.Component:
    """Render index for the advanced search page."""
    return page(
        rx.hstack(
            sidebar(), search_results(), align="stretch", style=rx.Style(flex="1")
        )
    )
