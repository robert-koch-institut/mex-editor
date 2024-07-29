import reflex as rx

from mex.editor.edit.state import EditableField, EditablePrimarySource, EditState
from mex.editor.layout import page


def editable_value(value: str) -> rx.Component:
    """Return a single card for editing one value."""
    return rx.card(
        value,
        style={"width": "30vw"},
    )


def editable_primary_source(model: EditablePrimarySource) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        rx.card(
            model.name,
            style={"width": "15vw"},
        ),
        rx.vstack(
            rx.foreach(
                model.values,
                editable_value,
            )
        ),
    )


def editable_field(model: EditableField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            model.name,
            style={"width": "15vw"},
        ),
        rx.foreach(
            model.values,
            editable_primary_source,
        ),
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.section(
            rx.heading(
                EditState.item_title,
                custom_attrs={"data-testid": "edit-heading"},
                style={"margin": "1em 0"},
            ),
            rx.vstack(
                rx.foreach(
                    EditState.fields,
                    editable_field,
                ),
            ),
            on_mount=EditState.refresh,
            style={"width": "100%"},
            custom_attrs={"data-testid": "edit-section"},
        ),
    )
