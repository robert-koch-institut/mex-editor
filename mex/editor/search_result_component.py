from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import reflex as rx
from reflex.event import EventCallback

from mex.editor.components import (
    icon_by_stem_type,
    render_additional_titles,
    render_title,
    render_value,
)
from mex.editor.models import EditorValue, SearchResult
from mex.editor.pagination_component import PaginationOptions, pagination


@dataclass
class SearchResultListItemOptions:
    """Options for rendering a search result list item."""

    enable_show_all_properties: bool = False
    on_toggle_show_all_properties: EventCallback[SearchResult, int] | None = None

    enable_title_href: bool = False

    render_title_fn: Callable[[SearchResult, int], rx.Component] | None = None
    render_prepend_fn: Callable[[SearchResult, int], rx.Component] | None = None
    render_append_fn: Callable[[SearchResult, int], rx.Component] | None = None


@dataclass
class SearchResultListOptions:
    """Options for rendering a search result list."""

    item_options: SearchResultListItemOptions = field(
        default_factory=SearchResultListItemOptions
    )


def search_result_list(
    items: list[SearchResult] | rx.Var[list[SearchResult]],
    options: SearchResultListOptions | None = None,
    **kwargs: dict[str, Any],
) -> rx.Component:
    """Render a list of search result items."""
    component_name = "search-result-list"
    options = options or SearchResultListOptions()

    style = rx.Style(overflow="auto")
    input_style = kwargs.pop("style", rx.Style())
    style.update(input_style)

    def render_properties(
        properties: list[EditorValue], property_type: str
    ) -> rx.Component:
        """Render a list of properties."""
        return rx.hstack(
            rx.foreach(
                properties,
                render_value,
            ),
            style=rx.Style(
                color="var(--gray-12)",
                fontWeight="var(--font-weight-light)",
            ),
            wrap="wrap",
            align="center",
            custom_attrs={
                "data-testid": f"{component_name}-properties-{property_type}"
            },
        )

    def search_result_item(
        item: SearchResult, index: int, options: SearchResultListItemOptions
    ) -> rx.Component:
        """Render a search result item."""
        title = render_title(item.title[0])

        title_line_children = [
            icon_by_stem_type(
                item.stem_type,
                size=22,
                style=rx.Style(color=rx.color("accent", 11)),
            ),
            rx.link(
                title,
                href=f"/item/{item.identifier}",
            )
            if options.enable_title_href
            else title,
            render_additional_titles(item.title[1:]),
        ]
        if options.enable_show_all_properties and options.on_toggle_show_all_properties:
            title_line_children.append(
                rx.button(
                    rx.icon(
                        rx.cond(
                            item.show_all_properties,
                            "minimize_2",
                            "maximize_2",
                        ),
                        style=rx.Style(width="1em", height="1em"),
                    ),
                    color_scheme="gray",
                    variant="surface",
                    size="1",
                    on_click=options.on_toggle_show_all_properties(item, index),
                )
            )

        if options.render_title_fn:
            title_line_children.append(options.render_title_fn(item, index))

        vstack_children: list[rx.Component] = [
            rx.hstack(*title_line_children, align="center")
        ]
        if options.enable_show_all_properties:
            vstack_children.append(
                rx.cond(
                    item.show_all_properties,
                    render_properties(item.all_properties, "all"),
                    render_properties(item.preview, "preview"),
                )
            )
        else:
            vstack_children.append(render_properties(item.preview, "preview"))

        card_content = []
        if options.render_prepend_fn:
            card_content.append(options.render_prepend_fn(item, index))

        card_content.append(
            rx.vstack(
                *vstack_children,
                align="stretch",
                style=rx.Style(width="100%", flex="1", min_width="0"),
            )
        )

        if options.render_append_fn:
            card_content.append(options.render_append_fn(item, index))

        return rx.card(
            rx.hstack(
                *card_content,
                align="stretch",
            ),
            class_name="search-result-card",
            custom_attrs={"data-testid": f"{component_name}-item-{item.identifier}"},
            style=rx.Style(width="100%", flex="1 0 auto", min_height="0"),
        )

    return rx.cond(
        items,
        rx.vstack(
            rx.foreach(
                items, lambda x, i: search_result_item(x, i, options.item_options)
            ),
            style=style,
            custom_attrs={"data-testid": f"{component_name}"},
        ),
    )


def search_result_summary(summary_text: rx.Var[str]) -> rx.Component:
    """Render the search result summary text."""
    return rx.text(
        summary_text,
        # SearchState.label_result_summary_format,
        style=rx.Style(
            color="var(--gray-12)",
            fontWeight="var(--font-weight-bold)",
            margin="var(--space-4)",
            userSelect="none",
        ),
        custom_attrs={"data-testid": "search-result-summary"},
    )


@dataclass
class SearchResultComponentOptions:
    """Options for the search result component."""

    summary_text: rx.Var[str]
    list: SearchResultListOptions
    pagination: PaginationOptions | None = None


def search_result_component(
    result: rx.Var[list[SearchResult]] | list[SearchResult],
    options: SearchResultComponentOptions,
    **kwargs: dict[str, Any],
) -> rx.Component:
    """Render the search result component with summary, list, and pagination."""
    style = rx.Style(overflow="auto")
    input_style = kwargs.pop("style", rx.Style())
    style.update(input_style)

    content = [
        rx.center(search_result_summary(options.summary_text)),
        search_result_list(
            result,
            options.list,
        ),
    ]
    if options.pagination:
        content.append(rx.center(pagination(options.pagination)))

    return rx.vstack(
        *content,
        spacing="4",
        custom_attrs={"data-testid": "search-result-component"},
        align="stretch",
        style=style,
    )
