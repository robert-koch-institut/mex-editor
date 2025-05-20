from typing import cast

import reflex as rx

from mex.editor.components import render_span
from mex.editor.create.state import CreateState
from mex.editor.edit.models import (
    EditorField,
    InputConfig,
    ValidationMessage,
)
from mex.editor.layout import page
from mex.editor.models import EditorValue


def remove_additive_button(
    field_name: str,
    index: int,
) -> rx.Component:
    """Render a button to remove an additive value."""
    return rx.button(
        rx.icon(
            tag="circle-minus",
            height="1rem",
            width="1rem",
        ),
        f"Remove {field_name}",
        color_scheme="tomato",
        variant="soft",
        size="1",
        on_click=cast("CreateState", CreateState).remove_additive_value(
            field_name, index
        ),
        custom_attrs={
            "data-testid": f"additive-rule-{field_name}-{index}-remove-button"
        },
    )


def editor_value_input(
    field_name: str, input_config: InputConfig, index: int, value: EditorValue
) -> rx.Component:
    """Return an input mask for additive rules."""
    return rx.hstack(
        rx.cond(
            input_config.editable_href,
            rx.input(
                placeholder="URL",
                value=value.href,
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
                value=value.text,
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
            rx.fragment(
                rx.foreach(
                    input_config.badge_titles,
                    render_span,
                ),
                rx.box(
                    rx.select(
                        input_config.badge_options,
                        value=cast("rx.Var", value.badge)
                        | cast("rx.Var", input_config.badge_default),
                        size="1",
                        variant="soft",
                        radius="large",
                        color_scheme="gray",
                        on_change=cast("CreateState", CreateState).set_badge_value(
                            field_name, index
                        ),
                        custom_attrs={
                            "data-testid": f"additive-rule-{field_name}-{index}-badge"
                        },
                    ),
                ),
            ),
        ),
        remove_additive_button(
            field_name,
            index,
        ),
    )


def new_additive_button(
    field_name: str,
    primary_source_identifier: str,
) -> rx.Component:
    """Render a button for adding new additive rules to a given field."""
    return rx.card(
        rx.button(
            rx.icon(
                tag="circle-plus",
                height="1rem",
                width="1rem",
            ),
            f"New {field_name}",
            color_scheme="jade",
            variant="soft",
            size="1",
            on_click=cast("CreateState", CreateState).add_additive_value(field_name),
            custom_attrs={
                "data-testid": f"new-additive-{field_name}-{primary_source_identifier}"
            },
        ),
        style={"width": "100%"},
    )


def editor_field(
    field: EditorField,
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
                rx.foreach(
                    primary_source.editor_values,
                    lambda value, index: editor_value_input(
                        field.name,
                        cast("InputConfig", primary_source.input_config),
                        index,
                        value,
                    ),
                ),
            ),
            rx.cond(
                primary_source.input_config.allow_additive,
                new_additive_button(
                    field.name,
                    primary_source.identifier,
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
                    ["Resource"],  # move to state
                    value=CreateState.entity_type,
                    on_change=cast("CreateState", CreateState).set_entity_type,
                ),
            ),
            rx.foreach(
                CreateState.fields,
                lambda field: editor_field(
                    field,
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


def validation_message(error: ValidationMessage) -> rx.Component:
    """Render a single validation error message."""
    return rx.data_list.item(
        rx.data_list.label(error.field_name),
        rx.data_list.value(
            render_span(error.message),
            render_span(" (Input: "),
            rx.code(error.input),
            render_span(")"),
            style={"display": "inline"},
        ),
        align="center",
    )


def validation_errors() -> rx.Component:
    """Return an overlay showing validation errors."""
    return rx.box(
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title("Validation Errors"),
                rx.alert_dialog.description(
                    rx.card(
                        rx.data_list.root(
                            rx.foreach(
                                CreateState.validation_messages, validation_message
                            )
                        ),
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Close",
                        on_click=CreateState.clear_validation_messages,
                        style={"margin": "var(--line-height-1) 0"},
                        custom_attrs={"data-testid": "close-validation-errors-button"},
                    ),
                    style={"justify-content": "flex-end"},
                ),
            ),
            open=cast("rx.vars.ArrayVar", CreateState.validation_messages).bool(),
        )
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        "Save",
        color_scheme="jade",
        size="3",
        on_click=CreateState.submit_rule_set,
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
            validation_errors(),
            style={"width": "100%"},
        ),
    )
