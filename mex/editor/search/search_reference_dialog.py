from collections.abc import Generator
from typing import Any
from reflex.app import EventSpec
from requests import HTTPError
from mex.common.backend_api.connector import BackendApiConnector

import reflex as rx

from mex.editor.components import (
    PaginationButtonOptions,
    PaginationOptions,
    PaginationPageOptions,
    PaginationStateMixin,
    icon_by_stem_type,
    pagination_abstract,
    render_additional_titles,
    render_search_preview,
    render_title,
)
from mex.editor.exceptions import escalate_error
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results


class SearchReferenceDialog(rx.ComponentState, PaginationStateMixin):
    is_loading: bool = False
    limit = 10

    query: str = ""
    entity_types: list[str] = []
    # limit: int = 10

    result: list[SearchResult] = []
    # current_page: int = 1
    # total: int = 0

    @rx.event
    def update_query(self, value: str) -> None:
        self.query = value

    @rx.event
    def refresh_on_enter(self, key: str) -> Generator[EventSpec | None, None, None]:
        if key.lower() == "enter":
            yield from self.search()

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        if self.is_loading:
            return
        connector = BackendApiConnector.get()

        skip = self.limit * (self.current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.query,
                entity_type=None,  # self.entity_types,
                skip=skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.result = []
            self.total = 0
            self.current_page = 1
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.result = transform_models_to_results(response.items)
            self.total = response.total

        # print("REFRESH", response)

    @classmethod
    def get_component(cls, **props) -> rx.Component:
        pagination_opts = PaginationOptions.create(
            cls, cls.search, cls.search, cls.search
        )

        def render_result_item(item: SearchResult) -> rx.Component:
            """Render a single merged item search result."""
            return rx.card(
                rx.vstack(
                    rx.hstack(
                        icon_by_stem_type(
                            item.stem_type,
                            size=22,
                            style=rx.Style(color=rx.color("accent", 11)),
                        ),
                        render_title(item.title[0]),
                        render_additional_titles(item.title[1:]),
                    ),
                    render_search_preview(item.preview),
                    style=rx.Style(width="100%"),
                ),
                class_name="search-result-card",
                custom_attrs={"data-testid": f"result-{item.identifier}"},
                style=rx.Style(width="100%", flex="1 0 auto", min_height="0"),
            )

        return rx.dialog.root(
            rx.dialog.trigger(rx.button(rx.icon("search"))),
            rx.dialog.content(
                rx.dialog.title("Suche nach Entitäten"),
                rx.dialog.description(
                    f"Suchen sie Entätiten vom Typ {cls.entity_types}.",
                    size="2",
                    margin_bottom="16px",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            value=cls.query,
                            on_change=cls.update_query,
                            on_key_down=cls.refresh_on_enter,
                            custom_attrs={"data-focusme": ""},
                        ),
                        rx.button(
                            rx.icon("search"),
                            type="submit",
                            variant="surface",
                            disabled=cls.is_loading,
                            on_click=cls.search,
                            custom_attrs={"data-testid": "search-button"},
                        ),
                        pagination_abstract(pagination_opts),
                    ),
                    rx.vstack(
                        rx.foreach(cls.result, render_result_item),
                        style=rx.Style(
                            {
                                "overflow": "auto",
                                "max-height": "50vh",
                            }
                        ),
                    ),
                    style=rx.Style(align_items="stretch"),
                ),
                style=rx.Style({"max-width": "55vw !important"}),
            ),
        )
