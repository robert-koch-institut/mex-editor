from typing import cast

import reflex as rx

from mex.editor.components import fixed_value
from mex.editor.edit.models import EditableField, EditablePrimarySource, FixedValue
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def fixed_value_card(
    field_name: str,
    primary_source: str | None,
    index: int,
    value: FixedValue,
) -> rx.Component:
    """Return a card containing a single fixed value."""
    return rx.card(
        rx.hstack(
            fixed_value(value),
            rx.switch(
                checked=value.enabled,
                disabled=~cast(rx.vars.ArrayVar, EditState.editable_fields).contains(
                    field_name
                ),
                on_change=lambda enabled: cast(EditState, EditState).toggle_field_value(
                    field_name,
                    value,
                    enabled,
                ),
            ),
        ),
        style={"width": "30vw"},
        custom_attrs={"data-testid": f"value-{field_name}_{primary_source}_{index}"},
    )


def editable_primary_source(
    field_name: str,
    model: EditablePrimarySource,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        rx.card(
            rx.hstack(
                fixed_value(model.name),
                rx.switch(
                    checked=model.enabled,
                    disabled=~cast(
                        rx.vars.ArrayVar, EditState.editable_fields
                    ).contains(field_name),
                    on_change=lambda enabled: cast(
                        EditState, EditState
                    ).toggle_primary_source(
                        field_name,
                        cast(str, model.name.href),
                        enabled,
                    ),
                ),
            ),
            style={"width": "20vw"},
            custom_attrs={
                "data-testid": f"primary-source-{field_name}_{model.name.text}"
            },
        ),
        rx.vstack(
            rx.foreach(
                model.editor_values,
                lambda value, index: fixed_value_card(
                    field_name,
                    model.name.text,
                    index,
                    value,
                ),
            )
        ),
    )


def editable_field(model: EditableField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            rx.text(model.name),
            style={"width": "15vw"},
            custom_attrs={"data-testid": f"field-{model.name}"},
        ),
        rx.foreach(
            model.primary_sources,
            lambda primary_source: editable_primary_source(
                model.name,
                primary_source,
            ),
        ),
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
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.box(
            rx.heading(
                rx.hstack(
                    rx.foreach(
                        EditState.item_title,
                        fixed_value,
                    )
                ),
                custom_attrs={"data-testid": "edit-heading"},
                style={
                    "margin": "1em 0",
                    "whiteSpace": "nowrap",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "maxWidth": "80%",
                },
            ),
            rx.vstack(
                rx.foreach(
                    EditState.fields,
                    editable_field,
                ),
                submit_button(),
            ),
            style={"width": "100%", "margin": "0 2em 1em"},
            custom_attrs={"data-testid": "edit-section"},
        ),
    )
