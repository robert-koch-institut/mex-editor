from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.edit.models import (
    EditorField,
    EditorPrimarySource,
    EditorValue,
    InputConfig,
)
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def editor_value_switch(
    field_name: str,
    primary_source: str | None,
    value: EditorValue,
    index: int,
) -> rx.Component:
    """Return a switch for toggling subtractive rules."""
    return rx.switch(
        checked=value.enabled,
        on_change=cast(EditState, EditState).toggle_field_value(field_name, value),
        custom_attrs={"data-testid": f"switch-{field_name}-{primary_source}-{index}"},
        color_scheme="jade",
    )


def editor_value_card(
    field_name: str,
    primary_source: str | None,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Return a card containing a single editor value."""
    return rx.card(
        rx.hstack(
            render_value(value),
            rx.cond(
                cast(rx.vars.ArrayVar, EditState.editor_fields).contains(field_name),
                editor_value_switch(field_name, primary_source, value, index),
            ),
        ),
        style={"width": "100%"},
        custom_attrs={"data-testid": f"value-{field_name}-{primary_source}-{index}"},
    )


def editor_additive_string(
    field_name: str,
    primary_source: str | None,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Render an input component for additive string rules."""
    return rx.card(
        rx.hstack(
            rx.input(
                placeholder=field_name,
                value=value.text,
                on_change=cast(EditState, EditState).set_string_value(
                    field_name, index
                ),
                style={"margin": "calc(-1 * var(--space-1))"},
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-string-input"
                },
            ),
            rx.button(
                rx.icon(
                    tag="circle-minus",
                    height="1rem",
                    width="1rem",
                ),
                "Remove",
                color_scheme="tomato",
                variant="soft",
                size="1",
                on_click=cast(EditState, EditState).remove_additive_value(
                    field_name, index
                ),
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-minus-button"
                },
            ),
            rx.cond(
                cast(rx.vars.ArrayVar, EditState.editor_fields).contains(field_name),
                editor_value_switch(field_name, primary_source, value, index),
            ),
        ),
        style={"width": "100%"},
    )


def editor_additive_rules(
    field_name: str,
    primary_source: str | None,
    input_config: InputConfig,
    additive_values: list[EditorValue],
) -> rx.Component:
    """Return a component to create additive rules."""
    return rx.cond(
        input_config.data_type == "string",
        rx.fragment(
            rx.foreach(
                additive_values,
                lambda value, index: editor_additive_string(
                    field_name,
                    primary_source,
                    index,
                    value,
                ),
            ),
            rx.card(
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
                    on_click=cast(EditState, EditState).add_additive_value(field_name),
                    custom_attrs={
                        "data-testid": f"additive-rule-{field_name}-plus-button"
                    },
                ),
                style={"width": "100%"},
            ),
        ),
    )


def primary_source_switch(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a switch for toggling preventive rules."""
    return rx.switch(
        checked=model.enabled,
        on_change=cast(EditState, EditState).toggle_primary_source(
            field_name, model.name.href
        ),
        custom_attrs={"data-testid": f"switch-{field_name}-{model.identifier}"},
        color_scheme="jade",
    )


def primary_source_name(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return the name of a primary source as a card with a preventive rule toggle."""
    return rx.card(
        rx.hstack(
            render_value(model.name),
            rx.cond(
                cast(rx.vars.ArrayVar, EditState.editor_fields).contains(field_name),
                primary_source_switch(field_name, model),
            ),
        ),
        style={"width": "25%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.name.text}-name"
        },
    )


def editor_primary_source(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        primary_source_name(field_name, model),
        rx.vstack(
            rx.foreach(
                model.editor_values,
                lambda value, index: editor_value_card(
                    field_name,
                    model.name.text,
                    index,
                    value,
                ),
            ),
            rx.cond(
                model.input_config,
                editor_additive_rules(
                    field_name,
                    model.name.text,
                    cast(InputConfig, model.input_config),
                    model.additive_values,
                ),
            ),
            style={"width": "100%"},
        ),
        style={"width": "100%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.name.text}",
        },
    )


def editor_field(model: EditorField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            rx.text(model.name),
            style={"width": "25%"},
            custom_attrs={"data-testid": f"field-{model.name}-name"},
        ),
        rx.vstack(
            rx.foreach(
                model.primary_sources,
                lambda primary_source: editor_primary_source(
                    model.name,
                    primary_source,
                ),
            ),
            style={"width": "100%"},
        ),
        style={"width": "100%"},
        custom_attrs={"data-testid": f"field-{model.name}"},
        role="row",
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        "Save",
        color_scheme="jade",
        size="3",
        on_click=EditState.submit_rule_set,
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def edit_heading() -> rx.Component:
    """Return the heading for the edit page."""
    return rx.heading(
        rx.hstack(
            rx.foreach(
                EditState.item_title,
                render_value,
            ),
        ),
        custom_attrs={"data-testid": "edit-heading"},
        style={
            "whiteSpace": "nowrap",
            "overflow": "hidden",
        },
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            edit_heading(),
            rx.foreach(
                EditState.fields,
                editor_field,
            ),
            rx.cond(
                EditState.fields,
                submit_button(),
            ),
            style={"width": "100%"},
        ),
    )
