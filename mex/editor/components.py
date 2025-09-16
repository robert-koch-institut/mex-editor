import reflex as rx

from mex.editor.ingest.state import IngestState
from mex.editor.rules.models import EditorValue
from mex.editor.search.state import SearchState
from mex.editor.state import State


def render_title(title: list[EditorValue]) -> rx.Component:
    """Render one title and if necessary a badge with tooltip and additional titles."""
    more_title = title[1:]
    return rx.hstack(
        render_value(title[0]),
        rx.cond(
            more_title,
            rx.hover_card.root(
                rx.hover_card.trigger(
                    rx.badge("+ additional titles"),
                    custom_attrs={"data-testid": "tooltip-additional-titles-trigger"},
                ),
                rx.hover_card.content(
                    rx.foreach(more_title, render_value),
                    custom_attrs={"data-testid": "tooltip-additional-titles"},
                ),
            ),
        ),
    )


def render_identifier(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.skeleton(
        rx.link(
            rx.cond(
                value.text,
                value.text,
                "Loading ...",
            ),
            on_click=State.navigate(value.href),
            high_contrast=True,
            role="link",
            class_name="truncate",
            title=value.text,
            custom_attrs={"data-href": value.href},
        ),
        loading=rx.cond(
            value.text,
            c1=False,
            c2=True,
        ),
    )


def render_external_link(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable external link that opens in a new tab."""
    return rx.link(
        rx.cond(
            value.text,
            value.text,
            value.href,
        ),
        href=f"{value.href}",
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
        rx.cond(
            value.text,
            render_span(value.text),
            render_span("Loading ..."),
        ),
        loading=rx.cond(
            value.text,
            c1=False,
            c2=True,
        ),
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


def pagination(state: type[IngestState | SearchState]) -> rx.Component:
    """Render pagination for navigating search results."""
    return rx.center(
        rx.button(
            rx.text("Previous"),
            on_click=[
                state.go_to_previous_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
            ],
            disabled=state.disable_previous_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-previous-button"},
            style={"minWidth": "10%"},
        ),
        rx.select(
            state.page_selection,
            value=f"{state.current_page}",
            on_change=[
                state.set_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
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
            ],
            disabled=state.disable_next_page,
            variant="surface",
            custom_attrs={"data-testid": "pagination-next-button"},
            style={"minWidth": "10%"},
        ),
        spacing="4",
        style={"width": "100%"},
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
