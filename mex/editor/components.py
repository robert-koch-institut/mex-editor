from collections.abc import Callable
from typing import Any

import reflex as rx

from mex.editor.ingest.state import IngestState
from mex.editor.rules.models import EditorValue
from mex.editor.search.state import SearchState
from mex.editor.state import State


def render_title(title: EditorValue) -> rx.Component:
    """Render one title in a container with hidden overflow."""
    return rx.box(
        render_value(title),
        style=rx.Style(
            fontWeight="var(--font-weight-bold)",
            overflow="hidden",
            whiteSpace="nowrap",
        ),
    )


def render_additional_titles(titles: list[EditorValue]) -> rx.Component:
    """Render one title and if necessary a badge with tooltip and additional titles."""
    return rx.cond(
        titles,
        rx.hover_card.root(
            rx.hover_card.trigger(
                rx.badge(
                    "+ additional titles",
                    style=rx.Style(margin="auto 0"),
                ),
                custom_attrs={"data-testid": "tooltip-additional-titles-trigger"},
            ),
            rx.hover_card.content(
                rx.foreach(titles, render_value),
                custom_attrs={"data-testid": "tooltip-additional-titles"},
            ),
        ),
    )


def render_search_preview(values: list[EditorValue]) -> rx.Component:
    """Render a horizontal stack of editor values for a search preview."""
    return rx.hstack(
        rx.foreach(
            values,
            render_value,
        ),
        style=rx.Style(
            color="var(--gray-12)",
            fontWeight="var(--font-weight-light)",
            whiteSpace="nowrap",
            overflow="hidden",
            textOverflow="ellipsis",
            maxWidth="100%",
        ),
    )


def render_identifier(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.skeleton(
        rx.link(
            value.text,
            on_click=State.navigate(value.href),  # type: ignore[misc]
            high_contrast=True,
            role="link",
            class_name="truncate",
            title=value.text,
            custom_attrs={"data-href": value.href},
        ),
        min_width="16ch",
        min_height="1lh",
        loading=rx.cond(value.text, c1=False, c2=True),
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
        title=value.text,
        class_name="truncate",
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
        class_name="truncate",
        title=text,
    )


def render_text(value: EditorValue) -> rx.Component:
    """Render an editor value as a text span."""
    return rx.skeleton(
        render_span(value.text),
        min_width="16ch",
        min_height="1lh",
        loading=rx.cond(value.text, c1=False, c2=True),
    )


def render_badge(text: str | None) -> rx.Component:
    """Render a generic badge with the given text."""
    return rx.badge(
        text,
        radius="large",
        variant="soft",
        color_scheme="gray",
        style=rx.Style(margin="auto 0"),
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


def pagination(
    state: type[IngestState | SearchState], *page_load_hooks: Callable[[], Any]
) -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous"),
            on_click=[
                state.go_to_previous_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
            disabled=state.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style=rx.Style(minWidth="10%"),
        ),
        rx.select(
            state.page_selection,
            value=f"{state.current_page}",
            on_change=[
                state.set_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
            disabled=state.disable_page_selection,
            custom_attrs={"data-testid": "pagination-page-select"},
        ),
        rx.button(
            rx.text("Next", weight="bold"),
            on_click=[
                state.go_to_next_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
            disabled=state.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style=rx.Style(minWidth="10%"),
        ),
        spacing="4",
        style=rx.Style(width="100%"),
    )


def icon_by_stem_type(
    stem_type: str | None = None,
    size: int | None = None,
    style: rx.Style | None = None,
) -> rx.Component | rx.Var[Any]:
    """Render an icon for the given stem type."""
    # Sigh, https://reflex.dev/docs/library/data-display/icon#using-dynamic-icon-tags
    return rx.match(
        stem_type,
        (
            "AccessPlatform",
            rx.icon("app_window", size=size, style=style, title=stem_type),
        ),
        (
            "Activity",
            rx.icon("circle_gauge", size=size, style=style, title=stem_type),
        ),
        (
            "BibliographicResource",
            rx.icon("book_marked", size=size, style=style, title=stem_type),
        ),
        (
            "Consent",
            rx.icon("badge_check", size=size, style=style, title=stem_type),
        ),
        (
            "ContactPoint",
            rx.icon("inbox", size=size, style=style, title=stem_type),
        ),
        (
            "Distribution",
            rx.icon("container", size=size, style=style, title=stem_type),
        ),
        (
            "Organization",
            rx.icon("building", size=size, style=style, title=stem_type),
        ),
        (
            "OrganizationalUnit",
            rx.icon("door_open", size=size, style=style, title=stem_type),
        ),
        (
            "Person",
            rx.icon("circle_user_round", size=size, style=style, title=stem_type),
        ),
        (
            "PrimarySource",
            rx.icon("hard_drive", size=size, style=style, title=stem_type),
        ),
        (
            "Resource",
            rx.icon("archive", size=size, style=style, title=stem_type),
        ),
        (
            "Variable",
            rx.icon("box", size=size, style=style, title=stem_type),
        ),
        (
            "VariableGroup",
            rx.icon("boxes", size=size, style=style, title=stem_type),
        ),
        rx.icon("file_question", size=size, style=style),
    )
