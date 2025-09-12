import reflex as rx

from mex.editor.create.state import CreateState
from mex.editor.layout import page
from mex.editor.rules.main import (
    editor_primary_source_stack,
    field_name,
    rule_page_header,
    validation_errors,
)
from mex.editor.rules.models import EditorField
from mex.editor.rules.state import RuleState


def editor_field(
    field: EditorField,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        field_name(field),
        rx.vstack(
            rx.foreach(
                field.primary_sources,
                lambda primary_source: rx.hstack(
                    editor_primary_source_stack(
                        field.name,
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
            "Create new",
            style=rx.Style(userSelect="none"),
        ),
        rx.select(
            CreateState.available_stem_types,
            value=RuleState.stem_type,
            on_change=[
                CreateState.set_stem_type,
                RuleState.refresh,
            ],
            custom_attrs={"data-testid": "entity-type-select"},
        ),
        custom_attrs={"data-testid": "create-heading"},
    )


def index() -> rx.Component:
    """Return the index for the create component."""
    return page(
        rx.vstack(
            rule_page_header(
                create_title(),
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
