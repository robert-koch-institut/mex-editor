import reflex as rx

from mex.editor.components import render_value
from mex.editor.edit.state import EditState
from mex.editor.layout import page
from mex.editor.rules.main import editor_field, rule_page_header, validation_errors
from mex.editor.rules.state import RuleState


def edit_title() -> rx.Component:
    """Return the title for the edit page."""
    return rx.heading(
        rx.hstack(
            rx.foreach(
                EditState.item_title,
                render_value,
            ),
            as_child=True,
        ),
        custom_attrs={"data-testid": "edit-heading"},
        style=rx.Style(userSelect="none"),
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            rule_page_header(
                edit_title(),
            ),
            rx.foreach(
                RuleState.fields,
                editor_field,
            ),
            validation_errors(),
            style=rx.Style(
                width="100%",
                marginTop="calc(2 * var(--space-6))",
            ),
        ),
    )
