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
                disabled=~EditState.editable_fields.contains(field_name),  # type: ignore[attr-defined]
                on_change=lambda enabled: EditState.toggle_field_value(  # type: ignore[call-arg]
                    field_name,  # type: ignore[arg-type]
                    value,
                    enabled,  # type: ignore[arg-type]
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
                    disabled=~EditState.editable_fields.contains(field_name),  # type: ignore[attr-defined]
                    on_change=lambda enabled: EditState.toggle_primary_source(  # type: ignore[call-arg]
                        field_name,  # type: ignore[arg-type]
                        model.name.href,  # type: ignore[arg-type]
                        enabled,  # type: ignore[arg-type]
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


def preview_tab() -> rx.Component:
    """Render a preview of the current merged item."""
    return rx.box(
        rx.foreach(
            EditState.preview_errors,
            lambda preview_error: rx.callout.root(
                rx.callout.icon(rx.icon(tag="triangle_alert")),
                rx.callout.text(preview_error),
                color_scheme="red",
                role="alert",
            ),
        ),
        rx.data_list.root(
            rx.foreach(
                EditState.preview,
                lambda editor_field: rx.data_list.item(
                    rx.data_list.label(editor_field.name),
                    rx.data_list.value(
                        rx.vstack(
                            rx.foreach(
                                editor_field.primary_sources,
                                lambda primary_source: rx.foreach(
                                    primary_source.editor_values,
                                    fixed_value,
                                ),
                            )
                        )
                    ),
                ),
            ),
        ),
    )


def debug_tab() -> rx.Component:
    """Render the raw editor fields alongside the raw rule set."""
    return rx.hstack(
        rx.vstack(
            rx.heading("Editor Fields", size="3"),
            rx.code_block(
                EditState.debug_editor_fields,
                language="json",
            ),
        ),
        rx.vstack(
            rx.heading("Rule Set", size="3"),
            rx.code_block(
                EditState.debug_rule_set,
                language="json",
            ),
        ),
    )


def preview_dialog() -> rx.Component:
    """Render a preview dialog with a preview tab and a debug tab."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Preview",
                color_scheme="jade",
                variant="soft",
                size="3",
                on_click=EditState.refresh_preview,
                style={"margin": "1em 0"},
            )
        ),
        rx.dialog.content(
            rx.dialog.close(
                rx.button(
                    rx.icon(tag="x"),
                    variant="ghost",
                    style={"position": "absolute", "right": "2em"},
                )
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Preview", value="preview"),
                    rx.tabs.trigger("Debug", value="debug"),
                ),
                rx.tabs.content(
                    preview_tab(),
                    value="preview",
                    style={"padding": "1em 0.25em", "minHeight": "60%"},
                ),
                rx.tabs.content(
                    debug_tab(),
                    value="debug",
                    style={"padding": "1em 0.25em", "minHeight": "60%"},
                ),
                default_value="preview",
            ),
            size="4",
            style={"maxWidth": "60%"},
        ),
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
                rx.hstack(
                    preview_dialog(),
                    submit_button(),
                ),
            ),
            style={"width": "100%", "margin": "0 2em 1em"},
            custom_attrs={"data-testid": "edit-section"},
        ),
    )
