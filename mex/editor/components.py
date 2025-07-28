from typing import cast

import reflex as rx

from mex.editor.rules.models import EditorValue


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
        rx.cond(
            value.text,
            value.text,
            value.href,
        ),
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


def render_span(text: str | None) -> rx.Component:
    """Render a generic span with the given text."""
    return rx.text(
        text,
        as_="span",
    )


def render_text(value: EditorValue) -> rx.Component:
    """Render an editor value as a text span."""
    return rx.skeleton(
        render_span(cast("rx.vars.StringVar", value.text) | "Loading ..."),
        loading=~cast("rx.vars.StringVar", value.text),
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


def icon_by_stem_type(
    stem_type: str | None,
    **props: int | str | rx.Color,
) -> rx.Component:
    """Render an icon for the given stem type."""
    # Sigh, https://reflex.dev/docs/library/data-display/icon#using-dynamic-icon-tags
    return rx.box(
        rx.match(
            stem_type,
            ("AccessPlatform", rx.icon("app_window", **props)),
            ("Activity", rx.icon("circle_gauge", **props)),
            ("BibliographicResource", rx.icon("book_marked", **props)),
            ("building", rx.icon("building", **props)),
            ("Consent", rx.icon("badge_check", **props)),
            ("ContactPoint", rx.icon("inbox", **props)),
            ("Distribution", rx.icon("container", **props)),
            ("Organization", rx.icon("building", **props)),
            ("OrganizationalUnit", rx.icon("door_open", **props)),
            ("Person", rx.icon("circle_user_round", **props)),
            ("PrimarySource", rx.icon("hard_drive", **props)),
            ("Resource", rx.icon("archive", **props)),
            ("Variable", rx.icon("box", **props)),
            ("VariableGroup", rx.icon("boxes", **props)),
            rx.icon("file_question", **props),
        ),
        title=stem_type,
    )
