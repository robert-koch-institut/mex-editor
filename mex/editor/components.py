import reflex as rx

from mex.editor.edit.models import FixedValue


def fixed_internal_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable internal link that reloads the edit page."""
    return rx.link(
        value.text,
        href=value.href,
        high_contrast=True,
        role="link",
    )


def fixed_external_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable external link that opens in a new window."""
    return rx.link(
        value.text,
        href=value.href,
        high_contrast=True,
        is_external=True,
        role="link",
    )


def fixed_link(value: FixedValue) -> rx.Component:
    """Render a fixed value as a clickable link that reloads the edit page."""
    return rx.cond(
        value.external,
        fixed_external_link(value),
        fixed_internal_link(value),
    )


def fixed_text(value: FixedValue) -> rx.Component:
    """Render a fixed value as a text span."""
    return rx.text(
        value.text,
        as_="span",
    )


def postfix_badge(value: FixedValue) -> rx.Component:
    """Render a generic badge after the fixed value."""
    return rx.badge(
        value.badge,
        radius="full",
        variant="surface",
        style={"margin": "auto 0"},
    )


def fixed_value(value: FixedValue) -> rx.Component:
    """Return a single fixed value."""
    return rx.hstack(
        rx.cond(
            value.href,
            fixed_link(value),
            fixed_text(value),
        ),
        rx.cond(
            value.badge,
            postfix_badge(value),
        ),
        spacing="1",
    )
