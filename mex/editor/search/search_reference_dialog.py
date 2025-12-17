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
from mex.editor.locale_service import LocaleService
from mex.editor.rules.models import FieldTranslation
from mex.editor.search.models import ReferenceDialogSearchResult
from mex.editor.search.transform import transform_models_to_dialog_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class SearchReferenceDialog(State, rx.ComponentState, PaginationStateMixin):
    limit = 10
    user_query: str = ""
    user_reference_types: list[str] = []

    expanded_properties: list[str] = []

    results: list[ReferenceDialogSearchResult] = []
    is_loading: bool = False

    _locale_service = LocaleService.get()

    @rx.var
    def label_user_reference_types(self) -> str:
        result = [
            f"{self.current_locale}: {x} ({self._locale_service.get_field_label(self.current_locale, '', 'contact')})"
            for x in self.user_reference_types
        ]
        return "|".join(result)

    @rx.event
    def toggle_properties(self, identifier: str) -> None:
        if identifier in self.expanded_properties:
            self.expanded_properties.remove(identifier)
        else:
            self.expanded_properties.append(identifier)

    @rx.event
    def dialog_open_close(self, is_open: bool) -> None:
        print("DIALOG OPEN CLOSE", is_open, self.results)
        if not is_open:
            self.user_query = ""
            self.user_reference_types = []
            self.results = []
            self.expanded_properties = []
            self.reset_pagination()

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.results:
            for value in [*result.preview, *result.title, *result.all_properties]:
                if value.identifier and not value.text:
                    async with self:
                        await resolve_editor_value(value)

    @rx.event
    def handle_submit(self, form_data: dict) -> Generator[EventSpec | None, None, None]:
        print("HANDLE SUBMIT. args formdata:", form_data)
        self.user_query = str(form_data.get("query", ""))
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
            self.results = None
            self.total = 0
            yield self.set_current_page(1)
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            self.results = transform_models_to_dialog_results(response.items)
            yield self.set_total(response.total)

        print("REFRESHED", self.total, self.current_page, self.limit)

    @classmethod
    def get_component(
        cls,
        on_identifier_selected: EventType[str],
        translated_field: FieldTranslation,  # reference_types: list[str], reference_field: str
    ) -> rx.Component:
        pagination_opts = PaginationOptions.create(cls, cls.search)

        print("CREATING DIALOG", translated_field.field.value_type)

        def render_result_item(item: ReferenceDialogSearchResult) -> rx.Component:
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
                            rx.button(
                                "expand_properties",
                                on_click=cls.toggle_properties(item.identifier),
                            ),
                        ),
                        rx.cond(
                            cls.expanded_properties.contains(item.identifier),
                            render_search_preview(item.all_properties),
                            # rx.foreach(item.all_properties, render_value),
                            render_search_preview(item.preview),
                        ),
                        style=rx.Style(width="100%", flex="1"),
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Auswählen",
                            on_click=on_identifier_selected(item.identifier),
                        ),
                    ),
                    align="center",
                ),
                class_name="search-result-card",
                custom_attrs={"data-testid": f"result-{item.identifier}"},
                style=rx.Style(width="100%", flex="1 0 auto", min_height="0"),
            )

        def render_result() -> rx.Component:
            return rx.cond(
                cls.is_loading,
                rx.spinner(),
                rx.cond(
                    cls.results,
                    rx.vstack(
                        rx.foreach(cls.results, render_result_item),
                        style=rx.Style(overflow="auto", max_height="50vh"),
                    ),
                    rx.center(
                        rx.text(
                            f"Leider wurden keine Ergebnisse für '{cls.user_query}' gefunden :(",
                            color_scheme="gray",
                            size="7",
                            style=rx.Style(padding="3em 0"),
                        ),
                    ),
                ),
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
                rx.dialog.title(
                    f"Suche nach Referenzen für {translated_field.label}..."
                ),
                rx.dialog.description(
                    rx.markdown(
                        f"Gültige Referenztypen: {cls.label_user_reference_types}\n\n"
                        "Klicken Sie anschließend auf 'Auswählen' in dem entprechenden "
                        "Eintrag um diesen auszuwählen.",
                    ),
                    size="2",
                    margin_bottom="16px",
                ),
                rx.vstack(
                    rx.form(
                        rx.vstack(
                            rx.hstack(
                                rx.hstack(
                                    rx.input(
                                        value=cls.user_query,
                                        on_change=cls.set_user_query,
                                        custom_attrs={"data-focusme": ""},
                                        placeholder="Suchtext",
                                        name="query",
                                        disabled=cls.is_loading,
                                        style=rx.Style(
                                            flex="1",
                                            max_width="380px",
                                            min_width="180px",
                                        ),
                                    ),
                                    rx.button(
                                        rx.icon("search"),
                                        type="submit",
                                        variant="surface",
                                        disabled=cls.is_loading,
                                        id="search-reference-dialog-form-submit-button",
                                        custom_attrs={"data-testid": "search-button"},
                                    ),
                                    style=rx.Style(flex="1"),
                                ),
                                rx.spacer(),
                                pagination_abstract(
                                    pagination_opts, style=rx.Style(flex="0")
                                ),
                                align="stretch",
                                justify="between",
                                style=rx.Style(width="100%"),
                            ),
                            rx.el.div(
                                rx.foreach(
                                    translated_field.field.value_type,
                                    lambda value, index: rx.checkbox(
                                        value,
                                        name=f"reference_type[{index}]",
                                        value=value,
                                        checked=True,
                                    ),
                                ),
                                style=rx.Style(display="None"),
                            ),
                        ),
                        id="search-reference-dialog-form",
                        on_submit=[cls.handle_submit, cls.resolve_identifiers],
                    ),
                    rx.script(
                        "setTimeout(() => document.getElementById('search-reference-dialog-form-submit-button').click(), 50)"
                    ),
                    render_result(),
                    align="stretch",
                ),
                style=rx.Style({"max-width": "62vw !important"}),
            ),
            on_open_change=cls.dialog_open_close,
        )
