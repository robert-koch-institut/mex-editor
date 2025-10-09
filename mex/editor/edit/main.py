import reflex as rx

from mex.editor.components import render_value
from mex.editor.edit.state import EditState
from mex.editor.layout import page
from mex.editor.rules.main import (
    editor_field,
    rule_page_header,
    validation_errors,
)
from mex.editor.rules.state import RuleState


def edit_title() -> rx.Component:
    """Return the title for the edit page."""
    return rx.heading(
        rx.hstack(
            rx.foreach(
                EditState.item_title,
                render_value,
            ),
        ),
        custom_attrs={"data-testid": "edit-heading"},
        style=rx.Style(userSelect="none"),
    )


def deactivate_all_switch() -> rx.Component:
    """Render a switch to deactivate all primary source and values."""
    return rx.hstack(
        rx.spacer(),
        "deactivate all",
        rx.switch(
            checked=EditState.any_primary_source_or_editor_value_enabled,
            on_change=EditState.disable_all_primary_source_and_editor_values,
            disabled=rx.cond(
                EditState.any_primary_source_or_editor_value_enabled,
                False,  # noqa: FBT003
                True,  # noqa: FBT003
            ),
            color_scheme="jade",
            custom_attrs={"data-testid": "deactivate-all-switch"},
        ),
        style=rx.Style(width="100%"),
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            rule_page_header(
                edit_title(),
            ),
            deactivate_all_switch(),
            rx.foreach(
                RuleState.translated_fields,
                editor_field,
            ),
            validation_errors(),
            style=rx.Style(
                width="100%",
                marginTop="calc(2 * var(--space-6))",
            ),
        ),
    )
