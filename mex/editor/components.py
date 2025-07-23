import reflex as rx

from mex.editor.ingest.state import IngestState
from mex.editor.rules.models import EditorValue
from mex.editor.search.state import SearchState


def render_identifier(value: EditorValue) -> rx.Component:
    """Render an editor value as a clickable internal link that loads the edit page."""
    return rx.skeleton(
        rx.link(
            rx.cond(
                value.text,
                value.text,
                "Loading ...",
            ),
            href=f"{value.href}",
            high_contrast=True,
            role="link",
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
