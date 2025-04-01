from typing import cast

import reflex as rx

from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.editor.components import render_span, render_value
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
    primary_source: EditorPrimarySource,
    value: EditorValue,
    index: int,
) -> rx.Component:
    """Return a switch for toggling subtractive rules."""
    return rx.switch(
        checked=value.enabled,
        on_change=cast("EditState", EditState).toggle_field_value(field_name, value),
        custom_attrs={
            "data-testid": f"switch-{field_name}-{primary_source.name.text}-{index}"
        },
        color_scheme=rx.cond(primary_source.enabled, "jade", "gray"),
    )


def editor_static_value(
    field_name: str,
    primary_source: EditorPrimarySource,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Render a static value with an optional subtractive rule switch."""
    return rx.hstack(
        render_value(value),
        editor_value_switch(field_name, primary_source, value, index),
    )


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
        on_click=cast("EditState", EditState).remove_additive_value(field_name, index),
        custom_attrs={
            "data-testid": f"additive-rule-{field_name}-{index}-remove-button"
        },
    )


def additive_rule_input(
    field_name: str,
    input_config: InputConfig,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Return an input mask for additive rules."""
    return rx.hstack(
        rx.cond(
            input_config.editable_href,
            rx.input(
                placeholder="URL",
                value=value.href,
                on_change=cast("EditState", EditState).set_href_value(
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
                on_change=cast("EditState", EditState).set_text_value(
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
                rx.select(
                    input_config.badge_options,
                    value=cast("rx.Var", value.badge)
                    | cast("rx.Var", input_config.badge_default),
                    size="1",
                    variant="soft",
                    radius="large",
                    color_scheme="gray",
                    on_change=cast("EditState", EditState).set_badge_value(
                        field_name, index
                    ),
                    custom_attrs={
                        "data-testid": f"additive-rule-{field_name}-{index}-badge"
                    },
                ),
            ),
        ),
        remove_additive_button(
            field_name,
            index,
        ),
    )


def editor_value_card(
    field_name: str,
    primary_source: EditorPrimarySource,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Return a card containing a single editor value."""
    return rx.card(
        rx.cond(
            primary_source.input_config.editable_text
            | primary_source.input_config.editable_href
            | primary_source.input_config.editable_badge,
            additive_rule_input(
                field_name,
                primary_source.input_config,
                index,
                value,
            ),
            editor_static_value(field_name, primary_source, index, value),
        ),
        background=rx.cond(
            primary_source.enabled & value.enabled, "inherit", "var(--gray-a4)"
        ),
        style={"width": "100%"},
        custom_attrs={
            "data-testid": f"value-{field_name}-{primary_source.name.text}-{index}"
        },
    )


def primary_source_switch(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a switch for toggling preventive rules."""
    return rx.switch(
        checked=model.enabled,
        on_change=cast("EditState", EditState).toggle_primary_source(
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
                model.identifier != MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
                primary_source_switch(field_name, model),
            ),
            wrap="wrap",
        ),
        background=rx.cond(model.enabled, "inherit", "var(--gray-a4)"),
        style={"width": "33%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.name.text}-name"
        },
    )


def new_additive_button(
    field_name: str,
    primary_source: str | None,
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
            on_click=cast("EditState", EditState).add_additive_value(field_name),
            custom_attrs={"data-testid": f"new-additive-{field_name}-{primary_source}"},
        ),
        style={"width": "100%"},
    )


def editor_primary_source_stack(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Render a stack of editor value cards and input elements for a primary source."""
    return rx.vstack(
        rx.foreach(
            model.editor_values,
            lambda value, index: editor_value_card(
                field_name,
                model,
                index,
                value,
            ),
        ),
        rx.cond(
            model.input_config.editable_text
            | model.input_config.editable_href
            | model.input_config.editable_badge,
            new_additive_button(
                field_name,
                model.name.text,
            ),
        ),
        style={"width": "100%"},
    )


def editor_primary_source(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        primary_source_name(
            field_name,
            model,
        ),
        editor_primary_source_stack(
            field_name,
            model,
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
            "width": "100%",
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
