from collections.abc import Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import reflex as rx
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.component_option_helper import build_pagination_options_for_mixin
from mex.editor.consent.state import ConsentState
from mex.editor.consent.transform import add_external_links_to_results
from mex.editor.exceptions import escalate_error
from mex.editor.models import SearchResult
from mex.editor.pagination_component import PaginationStateMixin, pagination
from mex.editor.search.transform import transform_models_to_results
from mex.editor.search_results_component import search_results_list
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value

if TYPE_CHECKING:
    from mex.common.models import AnyPreviewModel


@dataclass
class CategoryListConfig:
    """Config to store consent category list settings."""

    entity_type: str
    reference_fields: list[str]


CATEGORY_CONFIG: dict[str, CategoryListConfig] = {
    "resources": CategoryListConfig(
        "MergedResource", ["contact", "contributor", "creator"]
    ),
    "publications": CategoryListConfig(
        "MergedBibliographicResource", ["creator", "editor", "editorOfSeries"]
    ),
    "projects": CategoryListConfig("MergedActivity", ["contact", "involvedPerson"]),
}


class ConsentCategoryList(State, rx.ComponentState, PaginationStateMixin):
    """ComponentState to show user specific items with pagination."""

    config: CategoryListConfig | None = None
    category: str = ""
    is_loading = False
    items: list[SearchResult] = []
    limit = 5

    @rx.event
    def fetch_data(self) -> Generator[EventSpec | None]:
        """Fetch user-related data based on category."""
        if not self.merged_login_person or not self.config:
            yield None
            return

        connector = BackendApiConnector.get()

        self.is_loading = True
        yield None

        all_results: list[AnyPreviewModel] = []
        total = 0

        try:
            for ref_field in self.config.reference_fields:
                # TODO(FE): use advanced search method to fetch for multiple refs
                response = connector.fetch_preview_items(
                    query_string=None,
                    entity_type=[self.config.entity_type],
                    skip=self.skip,
                    limit=self.limit,
                    reference_field=ref_field,
                    referenced_identifier=[str(self.merged_login_person.identifier)],
                )
                all_results.extend(response.items)
                total += response.total

        except HTTPError as exc:
            self.is_loading = False
            self.set_current_page(1)  # type:ignore[operator]
            self.set_total(0)  # type:ignore[operator]
            self.items = []
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
            return

        transformed_results = transform_models_to_results(all_results)
        transformed_results = add_external_links_to_results(transformed_results)

        self.is_loading = False
        self.set_total(total)  # type:ignore[operator]
        self.items = transformed_results

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human-readable display values."""
        for result in self.items:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)

    @rx.event
    def initialize(self, category: str) -> Generator[EventSpec | None]:
        """Initialize the component state."""
        self.category = category
        config = CATEGORY_CONFIG.get(category)
        if not config:
            err_msg = f"Invalid category {category}."
            raise ValueError(err_msg)
        self.config = config

        yield type(self).fetch_data  # type:ignore[misc]
        yield type(self).resolve_identifiers

    @rx.event
    def cleanup(self) -> None:
        """Cleanup the component state."""
        self.category = ""
        self.items = []
        self.is_loading = False
        self.config = None
        self.reset_pagination()  # type: ignore[operator]

    @classmethod
    def get_component(
        cls, category: Literal["resources", "publications", "projects"]
    ) -> rx.Component:
        """Get the category list component."""
        title = getattr(ConsentState, f"label_{category}_title")

        return rx.fragment(
            rx.cond(
                cls.is_loading,
                rx.spinner(),
                rx.vstack(
                    rx.text(
                        title,
                        weight="bold",
                        style=rx.Style(
                            textTransform="uppercase",
                        ),
                    ),
                    search_results_list(cls.items),
                    pagination(
                        build_pagination_options_for_mixin(
                            cls,
                            cls.fetch_data(category),  # type:ignore[operator]
                            cls.resolve_identifiers,
                        )
                    ),
                    style=rx.Style(
                        textAlign="center",
                        marginBottom="var(--space-8)",
                    ),
                    custom_attrs={"data-testid": f"user-{category}"},
                ),
            ),
            on_mount=cls.initialize(category).debounce(500),  # type:ignore[operator]
            on_unmount=cls.cleanup,
        )
