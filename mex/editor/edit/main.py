from typing import cast

import reflex as rx

from mex.editor.components import render_value
from mex.editor.edit.models import EditorField, EditorPrimarySource, EditorValue
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def editor_value_switch(field_name: str, value: EditorValue) -> rx.Component:
    """Return a switch for toggling subtractive rules."""
    return rx.switch(
        checked=value.enabled,
        on_change=lambda enabled: cast(EditState, EditState).toggle_field_value(
            field_name,
            value,
            enabled,
        ),
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
                editor_value_switch(field_name, value),
            ),
        ),
        style={"width": "30vw"},
        custom_attrs={"data-testid": f"value-{field_name}-{primary_source}-{index}"},
    )


def primary_source_switch(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a switch for toggling preventive rules."""
    return rx.switch(
        checked=model.enabled,
        on_change=lambda enabled: cast(EditState, EditState).toggle_primary_source(
            field_name,
            cast(str, model.name.href),
            enabled,
        ),
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
        style={"width": "20vw"},
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
        ),
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.name.text}",
        },
    )


def editor_field(model: EditorField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            rx.text(model.name),
            style={"width": "15vw"},
            custom_attrs={"data-testid": f"field-{model.name}-name"},
        ),
        rx.vstack(
            rx.foreach(
                model.primary_sources,
                lambda primary_source: editor_primary_source(
                    model.name,
                    primary_source,
                ),
            )
        ),
        width="90vw",
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
        style={"margin": "1em 0"},
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
            "margin": "1em 0",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": "80vw",
        },
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.box(
            edit_heading(),
            rx.vstack(
                rx.foreach(
                    EditState.fields,
                    editor_field,
                ),
                rx.cond(
                    EditState.fields,
                    submit_button(),
                ),
            ),
            style={
                "width": "100%",
                "margin": "0 2em 1em",
            },
            custom_attrs={"data-testid": "edit-section"},
        ),
    )
