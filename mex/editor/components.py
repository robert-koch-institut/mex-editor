import reflex as rx

from mex.editor.edit.models import EditorValue


def render_internal_link(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.link(
        value.text,
        href=value.href,
        high_contrast=True,
        role="link",
    )


def render_external_link(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable external link that opens in a new tab."""
    return rx.link(
        value.text,
        href=value.href,
        high_contrast=True,
        is_external=True,
        role="link",
    )


def render_link(value: EditorValue) -> rx.Component:
    """Render an editor value as an internal or external link."""
    return rx.cond(
        value.external,
        render_external_link(value),
        render_internal_link(value),
    )


def render_span(text: str | None) -> rx.Component:
    """Render a generic span with the given text."""
    return rx.text(
        text,
        as_="span",
    )


def render_text(value: EditorValue) -> rx.Component:
    """Render an editor value as a text span."""
    return render_span(
        value.text,
    )


def render_badge(text: str | None) -> rx.Component:
    """Render a generic badge with the given text."""
    return rx.badge(
        text,
        radius="large",
        variant="soft",
        color_scheme="gray",
        style={"margin": "auto 0"},
    )


def render_value(value: EditorValue) -> rx.Component:
    """Render a single editor value."""
    return rx.hstack(
        rx.cond(
            value.href,
            render_link(value),
            render_text(value),
        ),
        rx.cond(
            value.badge,
            render_badge(value.badge),
        ),
        spacing="1",
    )
