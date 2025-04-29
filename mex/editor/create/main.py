from typing import cast

import reflex as rx

from mex.editor.create.state import CreateState
from mex.editor.edit.models import (
    EditorField,
    InputConfig,
)
from mex.editor.layout import page


def editor_value_input(
    field_name: str,
    input_config: InputConfig,
    index: int,
) -> rx.Component:
    """Return an input mask for additive rules."""
    return rx.hstack(
        rx.cond(
            input_config.editable_href,
            rx.input(
                placeholder="URL",
                on_change=cast("CreateState", CreateState).set_href_value(
                    field_name, index
                ),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "width": "100%",
                },
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-href"
                },
            ),
        ),
        rx.cond(
            input_config.editable_text,
            rx.input(
                placeholder="Text",
                on_change=cast("CreateState", CreateState).set_text_value(
                    field_name, index
                ),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "width": "100%",
                },
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-text"
                },
            ),
        ),
        rx.cond(
            input_config.editable_badge,
            rx.select(
                input_config.badge_options,
                value=input_config.badge_options[0],
                size="1",
                on_change=cast("CreateState", CreateState).set_badge_value(
                    field_name, index
                ),
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-badge"
                },
            ),
        ),
    )


def editor_field(
    field: EditorField,
    index: int,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.foreach(
        field.primary_sources,
        lambda primary_source: rx.hstack(
            rx.card(
                rx.text(field.name),
                style={"width": "25%"},
                custom_attrs={"data-testid": f"field-{field.name}-name"},
            ),
            rx.vstack(
                rx.cond(
                    primary_source.input_config,
                    editor_value_input(
                        field.name,
                        cast("InputConfig", primary_source.input_config),
                        index,
                    ),
                ),
            ),
            style={"width": "100%"},
            custom_attrs={"data-testid": f"field-{field.name}"},
            role="row",
        ),
    )


def create_input() -> rx.Component:
    """Return the input for the create page."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Entity Type", size="3"),
                rx.select(
                    ["ExtractedOrganization", "ExtractedResource"],
                    value=CreateState.entity_type,
                    on_change=CreateState.change_entity_type,
                ),
            ),
            rx.foreach(
                CreateState.fields,
                lambda field, index: editor_field(
                    field,
                    index,
                ),
            ),
        ),
        style={
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "padding": "var(--space-2)",
            "width": "100%",
        },
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        "Save",
        color_scheme="jade",
        size="3",
        on_click=CreateState.submit_new_item,
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def create_heading() -> rx.Component:
    """Return the heading for the create page."""
    return rx.heading(
        "Create New Item",
        custom_attrs={"data-testid": "create-heading"},
        style={
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "width": "100%",
        },
    )


def index() -> rx.Component:
    """Return the index for the create component."""
    return page(
        rx.vstack(
            create_heading(),
            create_input(),
            rx.cond(
                CreateState.fields,
                submit_button(),
            ),
            style={"width": "100%"},
        ),
    )
