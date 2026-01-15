import reflex as rx

from mex.editor.create.state import CreateState
from mex.editor.layout import page
from mex.editor.rules.main import (
    editor_primary_source_stack,
    field_name_card,
    rule_page_header,
    validation_errors,
)
from mex.editor.rules.state import FieldTranslation, RuleState


def editor_field(field_translation: FieldTranslation) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    field = field_translation.field
    return rx.hstack(
        field_name_card(field_translation),
        rx.vstack(
            rx.foreach(
                field.primary_sources,
                lambda primary_source: rx.hstack(
                    editor_primary_source_stack(
                        field_translation,
                        primary_source,
                    ),
                    style=rx.Style(width="100%"),
                ),
            ),
            style=rx.Style(width="100%"),
        ),
        style=rx.Style(
            width="100%",
            margin="var(--space-3) 0",
        ),
        custom_attrs={"data-testid": f"field-{field.name}"},
        role="row",
    )


def create_title() -> rx.Component:
    """Return the title for the create page."""
    return rx.hstack(
        rx.heading(
            CreateState.label_title_create_new,
            style=rx.Style(userSelect="none"),
        ),
        rx.select(
            CreateState.available_stem_types,
            value=rx.cond(RuleState.stem_type, RuleState.stem_type, ""),
            on_change=[
                CreateState.set_stem_type,
                RuleState.delete_local_state,
                RuleState.refresh,
                RuleState.update_local_state,
            ],
            custom_attrs={"data-testid": "entity-type-select"},
        ),
        custom_attrs={"data-testid": "create-heading"},
    )


def discard_draft_button() -> rx.Component:
    """Render a button to show discard draft dialog."""
    return rx.cond(
        CreateState.has_local_draft,
        rx.alert_dialog.root(
            rx.alert_dialog.trigger(
                rx.button(
                    CreateState.label_discard_draft_button,
                    color_scheme="tomato",
                ),
                custom_attrs={"data-testid": "discard-draft-dialog-button"},
            ),
            rx.alert_dialog.content(
                rx.alert_dialog.title(CreateState.label_discard_draft_dialog_title),
                rx.alert_dialog.description(
                    CreateState.label_discard_draft_dialog_description,
                    size="2",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(
                            CreateState.label_discard_draft_dialog_cancel_button,
                            variant="soft",
                            color_scheme="gray",
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.button(
                            CreateState.label_discard_draft_dialog_discard_button,
                            color_scheme="tomato",
                            variant="solid",
                            on_click=[
                                RuleState.delete_local_state,
                                rx.redirect(path="/create"),
                            ],
                            custom_attrs={"data-testid": "discard-draft-button"},
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
    """Return the index for the create component."""
    return page(
        rx.vstack(
            rule_page_header(
                rx.fragment(
                    create_title(),
                    discard_draft_button(),
                )
            ),
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
