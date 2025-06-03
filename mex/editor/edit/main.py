from typing import cast

import reflex as rx

from mex.editor.components import render_span, render_value
from mex.editor.edit.models import (
    EditorField,
    EditorPrimarySource,
    EditorValue,
    InputConfig,
    ValidationMessage,
)
from mex.editor.edit.state import EditState
from mex.editor.layout import page


def editor_value_switch(
    field_name: str,
    primary_source: EditorPrimarySource,
    value: EditorValue,
    index: int,
) -> rx.Component:
    """Return a switch for toggling subtractive rules."""
    return rx.switch(
        checked=value.enabled,
        on_change=cast("EditState", EditState).toggle_field_value(field_name, value),
        custom_attrs={
            "data-testid": f"switch-{field_name}-{primary_source.identifier}-{index}"
        },
        color_scheme=rx.cond(primary_source.enabled, "jade", "gray"),
    )


def editor_static_value(
    field_name: str,
    primary_source: EditorPrimarySource,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Render a static value with an optional subtractive rule switch."""
    return rx.hstack(
        render_value(value),
        editor_value_switch(field_name, primary_source, value, index),
    )


def remove_additive_button(
    field_name: str,
    index: int,
) -> rx.Component:
    """Render a button to remove an additive value."""
    return rx.button(
        rx.icon(
            tag="circle-minus",
            height="1rem",
            width="1rem",
        ),
        f"Remove {field_name}",
        color_scheme="tomato",
        variant="soft",
        size="1",
        on_click=cast("EditState", EditState).remove_additive_value(field_name, index),
        custom_attrs={
            "data-testid": f"additive-rule-{field_name}-{index}-remove-button"
        },
    )


def href_input(
    field_name: str,
    index: int,
    href: str | None,
) -> rx.Component:
    """Render an input component for editing a href attribute."""
    return rx.input(
        placeholder="URL",
        value=href,
        on_change=cast("EditState", EditState).set_href_value(field_name, index),
        style={
            "margin": "calc(-1 * var(--space-1))",
            "minWidth": "30%",
        },
        custom_attrs={"data-testid": f"additive-rule-{field_name}-{index}-href"},
    )


def text_input(
    field_name: str,
    index: int,
    text: str | None,
) -> rx.Component:
    """Render an input component for editing a text attribute."""
    return rx.input(
        placeholder="Text",
        value=text,
        on_change=cast("EditState", EditState).set_text_value(field_name, index),
        style={
            "margin": "calc(-1 * var(--space-1))",
            "minWidth": "30%",
        },
        custom_attrs={"data-testid": f"additive-rule-{field_name}-{index}-text"},
    )


def badge_input(
    field_name: str,
    index: int,
    input_config: InputConfig,
    badge: str | None,
) -> rx.Component:
    """Render an input component for editing a badge attribute."""
    return rx.fragment(
        rx.foreach(
            input_config.badge_titles,
            render_span,
        ),
        rx.box(
            rx.select(
                input_config.badge_options,
                value=cast("rx.Var", badge)
                | cast("rx.Var", input_config.badge_default),
                size="1",
                variant="soft",
                radius="large",
                color_scheme="gray",
                on_change=cast("EditState", EditState).set_badge_value(
                    field_name, index
                ),
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-badge"
                },
            ),
        ),
    )


def additive_rule_input(
    field_name: str,
    input_config: InputConfig,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Return an input mask for additive rules."""
    return rx.hstack(
        rx.cond(
            input_config.editable_href,
            rx.input(
                placeholder="URL",
                value=value.href,
                on_change=cast("EditState", EditState).set_href_value(
                    field_name, index
                ),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "minWidth": "30%",
                },
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-href"
                },
            ),
        ),
        rx.cond(
            input_config.editable_text,
            rx.input(
                placeholder="Text",
                value=value.text,
                on_change=cast("EditState", EditState).set_text_value(
                    field_name, index
                ),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "minWidth": "30%",
                },
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-text"
                },
            ),
        ),
        rx.cond(
            input_config.editable_identifier,
            rx.input(
                placeholder="Identifier",
                value=value.identifier,
                on_change=cast("EditState", EditState).set_identifier_value(
                    field_name, index
                ),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "minWidth": "30%",
                },
                custom_attrs={
                    "data-testid": f"additive-rule-{field_name}-{index}-identifier"
                },
            ),
        ),
        rx.cond(
            input_config.editable_badge,
            rx.fragment(
                rx.foreach(
                    input_config.badge_titles,
                    render_span,
                ),
                rx.box(
                    rx.select(
                        input_config.badge_options,
                        value=cast("rx.Var", value.badge)
                        | cast("rx.Var", input_config.badge_default),
                        size="1",
                        variant="soft",
                        radius="large",
                        color_scheme="gray",
                        on_change=cast("EditState", EditState).set_badge_value(
                            field_name, index
                        ),
                        custom_attrs={
                            "data-testid": f"additive-rule-{field_name}-{index}-badge"
                        },
                    ),
                ),
            ),
        ),
        remove_additive_button(
            field_name,
            index,
        ),
    )


def editor_value_card(
    field_name: str,
    primary_source: EditorPrimarySource,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Return a card containing a single editor value."""
    return rx.card(
        rx.cond(
            primary_source.input_config.allow_additive,
            additive_rule_input(
                field_name,
                primary_source.input_config,
                index,
                value,
            ),
            editor_static_value(field_name, primary_source, index, value),
        ),
        background=rx.cond(
            primary_source.enabled & value.enabled, "inherit", "var(--gray-a4)"
        ),
        style={"width": "100%"},
        custom_attrs={
            "data-testid": f"value-{field_name}-{primary_source.identifier}-{index}"
        },
    )


def primary_source_switch(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a switch for toggling preventive rules."""
    return rx.switch(
        checked=model.enabled,
        on_change=cast("EditState", EditState).toggle_primary_source(
            field_name, model.name.href
        ),
        custom_attrs={"data-testid": f"switch-{field_name}-{model.identifier}"},
        color_scheme="jade",
    )


def primary_source_name(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return the name of a primary source as a card with a preventive rule toggle."""
    return rx.card(
        rx.hstack(
            render_value(model.name),
            rx.spacer(),
            rx.cond(
                ~cast("rx.vars.BooleanVar", model.input_config.allow_additive),
                primary_source_switch(field_name, model),
            ),
            wrap="wrap",
        ),
        background=rx.cond(model.enabled, "inherit", "var(--gray-a4)"),
        style={"width": "33%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.identifier}-name"
        },
    )


def new_additive_button(
    field_name: str,
    primary_source_identifier: str,
) -> rx.Component:
    """Render a button for adding new additive rules to a given field."""
    return rx.card(
        rx.button(
            rx.icon(
                tag="circle-plus",
                height="1rem",
                width="1rem",
            ),
            f"New {field_name}",
            color_scheme="jade",
            variant="soft",
            size="1",
            on_click=cast("EditState", EditState).add_additive_value(field_name),
            custom_attrs={
                "data-testid": f"new-additive-{field_name}-{primary_source_identifier}"
            },
        ),
        style={"width": "100%"},
    )


def editor_primary_source_stack(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Render a stack of editor value cards and input elements for a primary source."""
    return rx.vstack(
        rx.foreach(
            model.editor_values,
            lambda value, index: editor_value_card(
                field_name,
                model,
                index,
                value,
            ),
        ),
        rx.cond(
            model.input_config.allow_additive,
            new_additive_button(
                field_name,
                model.identifier,
            ),
        ),
        style={"width": "100%"},
    )


def editor_primary_source(
    field_name: str,
    model: EditorPrimarySource,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        primary_source_name(
            field_name,
            model,
        ),
        editor_primary_source_stack(
            field_name,
            model,
        ),
        style={"width": "100%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{model.identifier}",
        },
    )


def editor_field(model: EditorField) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        rx.card(
            rx.text(model.name),
            style={"width": "25%"},
            custom_attrs={"data-testid": f"field-{model.name}-name"},
        ),
        rx.vstack(
            rx.foreach(
                model.primary_sources,
                lambda primary_source: editor_primary_source(
                    model.name,
                    primary_source,
                ),
            ),
            style={"width": "100%"},
        ),
        style={
            "width": "100%",
            "margin": "var(--space-3) 0",
        },
        custom_attrs={"data-testid": f"field-{model.name}"},
        role="row",
    )


def validation_message(error: ValidationMessage) -> rx.Component:
    """Render a single validation error message."""
    return rx.data_list.item(
        rx.data_list.label(error.field_name),
        rx.data_list.value(
            render_span(error.message),
            render_span(" (Input: "),
            rx.code(error.input),
            render_span(")"),
            style={"display": "inline"},
        ),
        align="center",
    )


def validation_errors() -> rx.Component:
    """Return an overlay showing validation errors."""
    return rx.box(
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title("Validation Errors"),
                rx.alert_dialog.description(
                    rx.card(
                        rx.data_list.root(
                            rx.foreach(
                                EditState.validation_messages, validation_message
                            )
                        ),
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Close",
                        on_click=EditState.clear_validation_messages,
                        style={"margin": "var(--line-height-1) 0"},
                        custom_attrs={"data-testid": "close-validation-errors-button"},
                    ),
                    style={"justify-content": "flex-end"},
                ),
            ),
            open=cast("rx.vars.ArrayVar", EditState.validation_messages).bool(),
        )
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        f"Save {EditState.stem_type}",
        size="3",
        color_scheme="jade",
        on_click=[
            EditState.submit_rule_set,
            EditState.resolve_identifiers,
        ],
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def edit_heading() -> rx.Component:
    """Return the heading for the edit page."""
    return rx.hstack(
        rx.heading(
            rx.hstack(
                rx.foreach(
                    EditState.item_title,
                    render_value,
                ),
                as_child=True,
            ),
            custom_attrs={"data-testid": "edit-heading"},
            style={
                "whiteSpace": "nowrap",
            },
        ),
        rx.spacer(),
        rx.cond(
            EditState.stem_type,
            submit_button(),
        ),
        style={
            "overflow": "hidden",
            "width": "100%",
            "top": "calc(var(--space-6) * 3)",
            "position": "fixed",
            "marginTop": "calc(-1 * var(--space-1))",
            "padding": "var(--space-4) 0",
            "backdropFilter": " var(--backdrop-filter-panel)",
            "backgroundColor": "var(--color-panel-translucent)",
            "maxWidth": "calc(var(--app-max-width) - var(--space-6) * 2)",
            "zIndex": "999",
            "alignItems": "baseline",
        },
    )


def index() -> rx.Component:
    """Return the index for the edit component."""
    return page(
        rx.vstack(
            edit_heading(),
            rx.foreach(
                EditState.fields,
                editor_field,
            ),
            validation_errors(),
            style={
                "width": "100%",
                "marginTop": "calc(2 * var(--space-6))",
            },
        ),
    )
