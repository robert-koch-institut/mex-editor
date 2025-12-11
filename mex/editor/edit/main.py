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
        ),
        custom_attrs={"data-testid": "edit-heading"},
        style=rx.Style(userSelect="none"),
    )


def toggle_all_switch() -> rx.Component:
    """Render a switch to toggle all primary source and values."""
    return rx.hstack(
        rx.spacer(),
        EditState.label_toggle_all,
        rx.switch(
            checked=EditState.any_primary_source_or_editor_value_enabled,
            on_change=EditState.toggle_all_primary_source_and_editor_values,
            color_scheme="jade",
            custom_attrs={"data-testid": "toggle-all-switch"},
        ),
        style=rx.Style(width="100%"),
    )


def discard_changes_button() -> rx.Component:
    """Render a button to show discard changes dialog."""
    return rx.cond(
        EditState.has_changes,
        rx.alert_dialog.root(
            rx.alert_dialog.trigger(
                rx.button(
                    EditState.label_discard_changes_button,
                    color_scheme="tomato",
                ),
                custom_attrs={"data-testid": "discard-changes-dialog-button"},
            ),
            rx.alert_dialog.content(
                rx.alert_dialog.title(EditState.label_discard_changes_dialog_title),
                rx.alert_dialog.description(
                    EditState.label_discard_changes_dialog_description,
                    size="2",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(
                            EditState.label_discard_changes_dialog_cancel_button,
                            variant="soft",
                            color_scheme="gray",
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.button(
                            EditState.label_discard_changes_dialog_discard_button,
                            color_scheme="tomato",
                            variant="solid",
                            on_click=[
                                RuleState.delete_local_state,
                                RuleState.refresh,
                                RuleState.resolve_identifiers,
                            ],
                            custom_attrs={"data-testid": "discard-changes-button"},
                        ),
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                style=rx.Style(max_width=450),
            ),
        ),
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            rule_page_header(rx.hstack(edit_title(), discard_changes_button())),
            toggle_all_switch(),
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
