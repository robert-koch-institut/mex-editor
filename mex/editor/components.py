from typing import cast

import reflex as rx

from mex.editor.edit.models import EditorValue


def render_identifier(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.skeleton(
        rx.link(
            cast("rx.vars.StringVar", value.text) | "Loading ...",
            href=value.href,
            high_contrast=True,
            role="link",
        ),
        loading=~cast("rx.vars.StringVar", value.text),
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
        value.identifier,
        render_identifier(value),
        render_external_link(value),
    )


def render_text(value: EditorValue) -> rx.Component:
    """Render an editor value as a text span."""
    return rx.skeleton(
        rx.text(
            cast("rx.vars.StringVar", value.text) | "Loading ...",
            as_="span",
        ),
        loading=~cast("rx.vars.StringVar", value.text),
    )


def render_badge(value: EditorValue) -> rx.Component:
    """Render a generic badge for an editor value."""
    return rx.badge(
        value.badge,
        radius="large",
        variant="soft",
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
            render_badge(value),
        ),
        spacing="1",
    )
