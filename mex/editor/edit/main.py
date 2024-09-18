import reflex as rx

from mex.editor.edit.models import EditableField, EditablePrimarySource, FixedValue
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def fixed_internal_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable internal link that reloads the edit page."""
    return rx.link(
        value.text,
        href=value.href,
        href_lang=value.language,
        high_contrast=True,
        on_click=EditState.refresh,
    )


def fixed_external_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable external link that opens in a new window."""
    return rx.link(
        value.text,
        href=value.href,
        href_lang=value.language,
        high_contrast=True,
        is_external=True,
    )


def fixed_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable link that reloads the edit page."""
    return rx.cond(
        value.external,
        fixed_external_link(value),
        fixed_internal_link(value),
    )


def fixed_text(value: FixedValue) -> rx.Component:
    """Render a fixed value as a text span with language attribute."""
    return rx.cond(
        value.text,
        rx.text(
            value.text,
            lang=value.language,
            as_="span",
        ),
        rx.icon("slash"),
    )


def language_badge(value: FixedValue) -> rx.Component:
    """Render a language badge for a fixed value."""
    return rx.badge(
        value.language,
        radius="full",
        variant="surface",
        style={
            "marginLeft": "0.5em",
            "textTransform": "uppercase",
        },
    )


def fixed_value(value: FixedValue) -> rx.Component:
    """Return a single card for one fixed value."""
    return rx.card(
        rx.cond(
            value.href,
            fixed_link(value),
            fixed_text(value),
        ),
        rx.cond(
            value.language,
            language_badge(value),
        ),
        style={"width": "30vw"},
    )


def editable_primary_source(model: EditablePrimarySource) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        fixed_value(model.name),
        rx.vstack(
            rx.foreach(
                model.values,
                fixed_value,
            )
        ),
    )


def editable_field(model: EditableField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            rx.text(model.name),
            style={"width": "15vw"},
        ),
        rx.foreach(
            model.primary_sources,
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
