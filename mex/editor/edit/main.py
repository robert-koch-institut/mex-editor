import reflex as rx

from mex.editor.components import render_value
from mex.editor.edit.state import EditState
from mex.editor.layout import page
from mex.editor.rules.main import (
    editor_field,
    flex1_col_style,
    rule_page_header,
    validation_errors,
)
from mex.editor.rules.state import RuleState
from mex.editor.search_results_component import (
    SearchResultsListItemOptions,
    SearchResultsListOptions,
    search_results_list,
)
from mex.editor.style_helper import flex3_style


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
        EditState.label_toggle_all,
        rx.switch(
            checked=EditState.any_primary_source_or_editor_value_enabled,
            on_change=EditState.toggle_all_primary_source_and_editor_values,
            color_scheme="jade",
            custom_attrs={"data-testid": "toggle-all-switch"},
        ),
    )


def delete_reset_button() -> rx.Component:
    """Render a button to delete or reset rules."""
    return rx.cond(
        EditState.delete_reset_mode != None,  # noqa: E711
        rx.button(
            rx.cond(EditState.is_deleting, rx.spinner()),
            rx.match(
                EditState.delete_reset_mode,
                ("reset", EditState.label_reset_rules_button),
                ("delete", EditState.label_delete_rules_button),
                "",
            ),
            disabled=EditState.is_deleting,
            on_click=EditState.delete_reset,
            color_scheme="red",
            variant="solid",
            custom_attrs={"data-testid": "delete-reset-button"},
        ),
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


def superseding_by_backward_card() -> rx.Component:
    """Render a card to show superseding items."""
    return rx.hstack(
        rx.card(
            rx.text(EditState.label_field_superseded_by_label),
            style=flex1_col_style,
            custom_attrs={"data-testid": "field-supersededBy-backward-name"},
            title=EditState.label_field_superseded_by_description,
        ),
        rx.card(
            rx.cond(
                EditState.superseded_by_backward,
                search_results_list(
                    EditState.superseded_by_backward,
                    SearchResultsListOptions(
                        item_options=SearchResultsListItemOptions(
                            enable_title_href=True
                        )
                    ),
                ),
                rx.text(EditState.label_field_superseded_by_empty),
            ),
            style=flex3_style,
        ),
        custom_attrs={"data-testid": "field-supersededBy-backward"},
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            rule_page_header(
                rx.hstack(
                    edit_title(),
                    discard_changes_button(),
                )
            ),
            rx.hstack(
                rx.spacer(),
                delete_reset_button(),
                toggle_all_switch(),
                align="center",
                style=rx.Style(
                    width="100%",
                ),
            ),
            rx.foreach(
                RuleState.translated_fields,
                editor_field,
            ),
            superseding_by_backward_card(),
            validation_errors(),
            align="stretch",
            style=rx.Style(
                flex="1", marginTop="calc(2 * var(--space-6))", overflow="auto"
            ),
        ),
    )
