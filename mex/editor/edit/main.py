import reflex as rx

from mex.editor.components import fixed_value
from mex.editor.edit.models import EditableField, EditablePrimarySource, FixedValue
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def fixed_value_card(
    field_name: str, primary_source: str | None, index: int, value: FixedValue
) -> rx.Component:
    """Return a card containing a single fixed value."""
    return rx.card(
        fixed_value(value),
        style={"width": "30vw"},
        custom_attrs={"data-testid": f"value-{field_name}_{primary_source}_{index}"},
    )


def editable_primary_source(
    field_name: str, model: EditablePrimarySource
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        rx.card(
            fixed_value(model.name),
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
            ),
            style={"width": "100%", "margin": "0 2em 1em"},
            custom_attrs={"data-testid": "edit-section"},
        ),
    )
