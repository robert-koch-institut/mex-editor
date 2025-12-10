from collections.abc import Generator

import reflex as rx
from reflex.app import EventSpec
from reflex.event import EventType
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.components import (
    PaginationOptions,
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
from mex.editor.utils import resolve_editor_value


class SearchReferenceDialog(rx.ComponentState, PaginationStateMixin):
    limit = 10
    user_query: str = ""
    user_reference_types: list[str] = []

    results: list[SearchResult] = []
    is_loading: bool = False

    @rx.event
    def dialog_open_close(self, is_open: bool) -> None:
        if not is_open:
            self.user_query = ""
            self.user_reference_types = []
            self.results = []

            self.reset_pagination()

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)

    @rx.event
    def handle_submit(self, form_data: dict) -> Generator[EventSpec | None, None, None]:
        print("HANDLE SUBMIT. args formdata:", form_data)
        self.user_query = form_data.get("query")
        self.user_reference_types = [
            value
            for key, value in form_data.items()
            if str(key).startswith("reference_type")
        ]

        yield from self.search()

    @rx.event
    def search(self) -> Generator[EventSpec | None, None, None]:
        if self.is_loading:
            return
        connector = BackendApiConnector.get()
        print("SEARCHING", self.user_query, self.user_reference_types)

        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=self.user_query,
                entity_type=self.user_reference_types,  # self.entity_types,
                skip=self.skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.results = []
            self.total = 0
            yield self.set_current_page(1)
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results = transform_models_to_results(response.items)
            yield self.set_total(response.total)

        print("REFRESHED", self.total, self.current_page, self.limit)

    @classmethod
    def get_component(
        cls, on_identifier_selected: EventType[str], reference_types: list[str]
    ) -> rx.Component:
        pagination_opts = PaginationOptions.create(cls, cls.search)

        print("CREATING DIALOG", reference_types)
        # cls.__fields__["_input_reference_types"].default = reference_types

        def render_result_item(item: SearchResult) -> rx.Component:
            """Render a single merged item search result."""
            return rx.card(
                rx.hstack(
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
                        style=rx.Style(width="100%", flex="1"),
                    ),
                    rx.dialog.close(
                        rx.button(
                            "SELECT",
                            on_click=on_identifier_selected(item.identifier),
                        ),
                    ),
                    align="center",
                ),
                class_name="search-result-card",
                custom_attrs={"data-testid": f"result-{item.identifier}"},
                style=rx.Style(width="100%", flex="1 0 auto", min_height="0"),
            )

        def render_reference_type_checkbox(value: str, index: int) -> rx.Component:
            return rx.checkbox(
                value, name=f"reference_type[{index}]", value=value, checked=True
            )

        return rx.dialog.root(
            rx.dialog.trigger(
                rx.icon_button(
                    rx.icon(
                        "search",
                        height="1rem",
                        width="1rem",
                    ),
                    variant="soft",
                    size="1",
                )
            ),
            rx.dialog.content(
                rx.dialog.title("Suche nach Referenzen..."),
                rx.dialog.description(
                    "Suchen sie nach Entitäten vom Typ",
                    rx.text(reference_types, style=rx.Style(font_weight="bold")),
                    size="2",
                    margin_bottom="16px",
                ),
                rx.vstack(
                    rx.form(
                        rx.vstack(
                            rx.hstack(
                                rx.input(
                                    value=cls.user_query,
                                    on_change=cls.set_user_query,
                                    # on_key_down=cls.refresh_on_enter,
                                    custom_attrs={"data-focusme": ""},
                                    name="query",
                                ),
                                rx.button(
                                    rx.icon("search"),
                                    type="submit",
                                    variant="surface",
                                    disabled=cls.is_loading,
                                    # on_click=cls.search,
                                    custom_attrs={"data-testid": "search-button"},
                                ),
                                pagination_abstract(pagination_opts),
                            ),
                            rx.foreach(reference_types, render_reference_type_checkbox),
                        ),
                        on_submit=cls.handle_submit,
                    ),
                    rx.vstack(
                        rx.foreach(cls.results, render_result_item),
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
            on_open_change=cls.dialog_open_close,
        )
