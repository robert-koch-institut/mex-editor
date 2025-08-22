from typing import cast

import reflex as rx

from mex.editor.components import icon_by_stem_type, render_span, render_value
from mex.editor.rules.models import (
    EditorField,
    EditorPrimarySource,
    EditorValue,
    InputConfig,
    ValidationMessage,
)
from mex.editor.rules.state import RuleState


def editor_value_switch(
    field_name: str,
    primary_source: EditorPrimarySource,
    value: EditorValue,
    index: int,
) -> rx.Component:
    """Return a switch for toggling subtractive rules."""
    return rx.switch(
        checked=value.enabled,
        on_change=RuleState.toggle_field_value(field_name, value),
        custom_attrs={
            "data-testid": f"switch-{field_name}-{primary_source.identifier}-{index}"
        },
        color_scheme=rx.cond(primary_source.enabled, "jade", "gray"),
    )


def editor_edit_button(
    field_name: str,
    primary_source: EditorPrimarySource,
    value: EditorValue,
    index: int,
) -> rx.Component:
    """Return a button for toggling editing."""
    return rx.icon_button(
        rx.cond(
            value.being_edited,
            rx.icon(
                "pencil-off",
                height="1rem",
                width="1rem",
            ),
            rx.icon(
                "pencil",
                height="1rem",
                width="1rem",
            ),
        ),
        variant="soft",
        size="1",
        on_click=[
            RuleState.toggle_field_value_editing(field_name, index),
            RuleState.resolve_identifiers,
        ],
        custom_attrs={
            "data-testid": (
                f"edit-toggle-{field_name}-{primary_source.identifier}-{index}"
            )
        },
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
        editor_value_switch(
            field_name,
            primary_source,
            value,
            index,
        ),
    )


def editor_additive_value(
    field_name: str,
    primary_source: EditorPrimarySource,
    index: int,
    value: EditorValue,
) -> rx.Component:
    """Render an additive value with buttons for editing and removal."""
    return rx.hstack(
        rx.hstack(
            rx.cond(
                value.being_edited,
                additive_rule_input(
                    field_name,
                    primary_source.input_config,
                    index,
                    value,
                ),
                render_value(value),
            ),
            rx.cond(
                primary_source.input_config.editable_identifier,
                editor_edit_button(field_name, primary_source, value, index),
            ),
            width="100%",
        ),
        remove_additive_button(
            field_name,
            index,
        ),
        custom_attrs={"data-testid": f"additive-rule-{field_name}-{index}"},
        spacing="8",
        width="100%",
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
        on_click=RuleState.remove_additive_value(field_name, index),
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
        on_change=RuleState.set_href_value(field_name, index),
        style={
            "margin": "calc(-1 * var(--space-1))",
            "width": "100%",
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
        on_change=RuleState.set_text_value(field_name, index),
        style={
            "margin": "calc(-1 * var(--space-1))",
            "width": "100%",
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
                value=rx.cond(
                    badge,
                    badge,
                    input_config.badge_default,
                ),
                size="1",
                variant="soft",
                radius="large",
                color_scheme="gray",
                on_change=RuleState.set_badge_value(field_name, index),
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
                on_change=RuleState.set_href_value(field_name, index),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "width": "100%",
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
                on_change=RuleState.set_text_value(field_name, index),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "width": "100%",
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
                on_change=RuleState.set_identifier_value(field_name, index),
                style={
                    "margin": "calc(-1 * var(--space-1))",
                    "width": "100%",
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
                        value=rx.cond(
                            value.badge,
                            value.badge,
                            input_config.badge_default,
                        ),
                        size="1",
                        variant="soft",
                        radius="large",
                        color_scheme="gray",
                        on_change=RuleState.set_badge_value(field_name, index),
                        custom_attrs={
                            "data-testid": f"additive-rule-{field_name}-{index}-badge"
                        },
                    ),
                ),
            ),
        ),
        width="100%",
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
            editor_additive_value(
                field_name,
                primary_source,
                index,
                value,
            ),
            editor_static_value(
                field_name,
                primary_source,
                index,
                value,
            ),
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
    primary_source: EditorPrimarySource,
) -> rx.Component:
    """Return a switch for toggling preventive rules."""
    return rx.switch(
        checked=primary_source.enabled,
        on_change=RuleState.toggle_primary_source(field_name, primary_source.name.href),
        custom_attrs={
            "data-testid": f"switch-{field_name}-{primary_source.identifier}"
        },
        color_scheme="jade",
    )


def primary_source_name(
    field_name: str,
    primary_source: EditorPrimarySource,
) -> rx.Component:
    """Return the name of a primary source as a card with a preventive rule toggle."""
    return rx.card(
        rx.hstack(
            render_value(primary_source.name),
            rx.spacer(),
            rx.cond(
                ~cast("rx.vars.BooleanVar", primary_source.input_config.allow_additive),
                primary_source_switch(
                    field_name,
                    primary_source,
                ),
            ),
            wrap="wrap",
        ),
        background=rx.cond(primary_source.enabled, "inherit", "var(--gray-a4)"),
        style={"width": "33%"},
        custom_attrs={
            "data-testid": (
                f"primary-source-{field_name}-{primary_source.identifier}-name"
            )
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
            on_click=RuleState.add_additive_value(field_name),
            custom_attrs={
                "data-testid": f"new-additive-{field_name}-{primary_source_identifier}"
            },
        ),
        style={"width": "100%"},
    )


def editor_primary_source_stack(
    field_name: str,
    primary_source: EditorPrimarySource,
) -> rx.Component:
    """Render a stack of editor value cards and input elements for a primary source."""
    return rx.vstack(
        rx.foreach(
            primary_source.editor_values,
            lambda value, index: editor_value_card(
                field_name,
                primary_source,
                index,
                value,
            ),
        ),
        rx.cond(
            primary_source.input_config.allow_additive,
            new_additive_button(
                field_name,
                primary_source.identifier,
            ),
        ),
        style={"width": "100%"},
    )


def editor_primary_source(
    field_name: str,
    primary_source: EditorPrimarySource,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one primary source."""
    return rx.hstack(
        primary_source_name(
            field_name,
            primary_source,
        ),
        editor_primary_source_stack(
            field_name,
            primary_source,
        ),
        style={"width": "100%"},
        custom_attrs={
            "data-testid": f"primary-source-{field_name}-{primary_source.identifier}",
        },
    )


def field_name(
    field: EditorField,
) -> rx.Component:
    """Return a card with a field name."""
    return rx.card(
        rx.hstack(
            rx.text(field.name),
            rx.cond(
                field.is_required,
                rx.text("*", style={"color": "red"}),
            ),
            spacing="1",
        ),
        style={"width": "25%"},
        custom_attrs={"data-testid": f"field-{field.name}-name"},
    )


def editor_field(
    field: EditorField,
) -> rx.Component:
    """Return a horizontal grid of cards for editing one field."""
    return rx.hstack(
        field_name(field),
        rx.vstack(
            rx.foreach(
                field.primary_sources,
                lambda primary_source: editor_primary_source(
                    field.name, primary_source
                ),
            ),
            style={"width": "100%"},
        ),
        style={
            "width": "100%",
            "margin": "var(--space-3) 0",
        },
        custom_attrs={"data-testid": f"field-{field.name}"},
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
    )


def validation_errors() -> rx.Component:
    """Return an overlay showing validation errors."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Validation Errors"),
            rx.alert_dialog.description(
                rx.card(
                    rx.data_list.root(
                        rx.foreach(RuleState.validation_messages, validation_message),
                        orientation="vertical",
                    ),
                ),
            ),
            rx.alert_dialog.action(
                rx.button(
                    "Close",
                    on_click=RuleState.clear_validation_messages,
                    style={"margin": "var(--line-height-1) 0"},
                    custom_attrs={"data-testid": "close-validation-errors-button"},
                ),
                style={"justifyContent": "flex-end"},
            ),
        ),
        open=cast("rx.vars.ArrayVar", RuleState.validation_messages).bool(),
    )


def submit_button() -> rx.Component:
    """Render a submit button to save the rule set."""
    return rx.button(
        f"Save {RuleState.stem_type}",
        size="3",
        color_scheme="jade",
        on_click=[
            RuleState.submit_rule_set,
            RuleState.resolve_identifiers,
        ],
        style={"margin": "var(--line-height-1) 0"},
        custom_attrs={"data-testid": "submit-button"},
    )


def rule_page_header(title: rx.Component) -> rx.Component:
    """Wrap the given title in a header component with a save button."""
    return rx.hstack(
        icon_by_stem_type(
            RuleState.stem_type,
            size=28,
            margin="auto 0",
        ),
        title,
        rx.spacer(),
        rx.cond(
            RuleState.stem_type,
            submit_button(),
        ),
        style={
            "alignItems": "baseline",
            "backdropFilter": " var(--backdrop-filter-panel)",
            "marginTop": "calc(-1 * var(--space-1))",
            "maxHeight": "6rem",
            "maxWidth": "calc(var(--app-max-width) - var(--space-6) * 2)",
            "overflow": "hidden",
            "padding": "var(--space-4) 0",
            "position": "fixed",
            "top": "calc(var(--space-6) * 3)",
            "width": "100%",
            "zIndex": "999",
        },
    )


def page_leave_js() -> rx.Component:
    """Render page leave java script import.

    Returns:
        rx.Component: The script component refrencing the
        '/page-leave-warn-unsaved-changes.js'
    """
    return rx.script(src="/page-leave-warn-unsaved-changes.js")
