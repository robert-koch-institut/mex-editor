import math
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Annotated, cast
from zoneinfo import ZoneInfo

import reflex as rx
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    AdditiveConsent,
    AnyPreviewModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
    ConsentRuleSetRequest,
)
from mex.common.types import (
    ConsentStatus,
    ConsentType,
    YearMonthDayTime,
)
from mex.editor.consent.transform import add_external_links_to_results
from mex.editor.exceptions import escalate_error
from mex.editor.label_var import label_var
from mex.editor.models import NavItem, SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value

CATEGORY_CONFIG = {
    "resources": {
        "entity_type": "MergedResource",
        "reference_fields": ["contact", "contributor", "creator"],
        "state_list": "user_resources",
        "state_total": "resources_total",
        "state_page": "resources_current_page",
    },
    "projects": {
        "entity_type": "MergedActivity",
        "reference_fields": ["contact", "involvedPerson"],
        "state_list": "user_projects",
        "state_total": "projects_total",
        "state_page": "projects_current_page",
    },
    "publications": {
        "entity_type": "MergedBibliographicResource",
        "reference_fields": ["creator", "editor", "editorOfSeries"],
        "state_list": "user_publications",
        "state_total": "publications_total",
        "state_page": "publications_current_page",
    },
}


class ConsentState(State):
    """State for the consent component."""

    user_projects: list[SearchResult] = []
    user_resources: list[SearchResult] = []
    user_publications: list[SearchResult] = []
    consent_status: SearchResult | None = None
    limit: Annotated[int, Field(ge=1, le=100)] = 5
    projects_total: Annotated[int, Field(ge=0)] = 0
    projects_current_page: Annotated[int, Field(ge=1)] = 1
    resources_total: Annotated[int, Field(ge=0)] = 0
    resources_current_page: Annotated[int, Field(ge=1)] = 1
    publications_total: Annotated[int, Field(ge=0)] = 0
    publications_current_page: Annotated[int, Field(ge=1)] = 1
    is_loading: bool = True

    @rx.var
    def _consent_nav_items(self) -> list[NavItem]:
        """Get the consent nav items."""
        return [
            NavItem(
                title=self.label_nav_bar_consent_navitem,
                path="/consent",
                raw_path="/consent/",
            ),
        ]

    @rx.var
    def consent_nav_items_translated(self) -> list[NavItem]:
        """Get the translated consent nav items, based on the current_locale.

        Returns:
            The translated consent nav items.
        """
        return [self._translate_nav_item(item) for item in self._consent_nav_items]

    @rx.var
    def consent_md(self) -> str:
        """Get the translated consent markdown, based on the current_locale.

        Returns:
            The translated consent markdown.
        """
        return Path(f"assets/consent_{self.current_locale}.md").read_text(
            encoding="utf-8"
        )

    @rx.var(cache=False)
    def disable_projects_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page for projects."""
        return self.projects_current_page <= 1

    @rx.var(cache=False)
    def disable_projects_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page for projects."""
        max_page = math.ceil(self.projects_total / self.limit)
        return self.projects_current_page >= max_page

    @rx.var(cache=False)
    def disable_resources_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page for resources."""
        return self.resources_current_page <= 1

    @rx.var(cache=False)
    def disable_resources_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page for resources."""
        max_page = math.ceil(self.resources_total / self.limit)
        return self.resources_current_page >= max_page

    @rx.var(cache=False)
    def disable_publications_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page for publications."""
        return self.publications_current_page <= 1

    @rx.var(cache=False)
    def disable_publications_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page for publications."""
        max_page = math.ceil(self.publications_total / self.limit)
        return self.publications_current_page >= max_page

    @rx.event
    def go_to_previous_page(self, category: str) -> None:
        """Navigate to the previous page for any category."""
        current_page = getattr(self, f"{category}_current_page")
        setattr(self, f"{category}_current_page", current_page - 1)

    @rx.event
    def go_to_next_page(self, category: str) -> None:
        """Navigate to the next page for any category."""
        current_page = getattr(self, f"{category}_current_page")
        setattr(self, f"{category}_current_page", current_page + 1)

    @rx.event
    def set_projects_page(self, page_number: str | int) -> None:
        """Set the current page for projects."""
        self.projects_current_page = int(page_number)

    @rx.event
    def set_resources_page(self, page_number: str | int) -> None:
        """Set the current page for resources."""
        self.resources_current_page = int(page_number)

    @rx.event
    def set_publications_page(self, page_number: str | int) -> None:
        """Set the current page for publications."""
        self.publications_current_page = int(page_number)

    @rx.var(cache=False)
    def projects_total_pages(self) -> list[str]:
        """Return a list of total pages for projects based on the result count."""
        return [f"{i + 1}" for i in range(math.ceil(self.projects_total / self.limit))]

    @rx.var(cache=False)
    def resources_total_pages(self) -> list[str]:
        """Return a list of total pages for resources based on the result count."""
        return [f"{i + 1}" for i in range(math.ceil(self.resources_total / self.limit))]

    @rx.var(cache=False)
    def publications_total_pages(self) -> list[str]:
        """Return a list of total pages for publications based on the result count."""
        return [
            f"{i + 1}" for i in range(math.ceil(self.publications_total / self.limit))
        ]

    @rx.var(cache=False)
    def consent_datetime(self) -> str:
        """Update datetime for a users consent status."""
        if not self.consent_status:
            return ""
        timestamp_str = self.consent_status.title[0].text
        timestamp_dt = datetime.fromisoformat(str(timestamp_str))
        timestamp_local = timestamp_dt.astimezone(ZoneInfo("Europe/Berlin"))
        return timestamp_local.strftime("%d.%m.%Y um %H:%M")

    @rx.event
    def get_all_data(self) -> Generator[EventSpec | None]:
        """Fetch all data for the user."""
        yield type(self).fetch_data("projects")  # type: ignore[operator]
        yield type(self).fetch_data("resources")  # type: ignore[operator]
        yield type(self).fetch_data("publications")  # type: ignore[operator]

    @rx.event
    def scroll_to_top(self) -> Generator[EventSpec | None]:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event
    def fetch_data(self, category: str) -> Generator[EventSpec | None]:
        """Fetch user-related data based on category."""
        if not self.merged_login_person:
            yield None
            return

        connector = BackendApiConnector.get()

        config = CATEGORY_CONFIG.get(category)
        if not config:
            msg = f"Unknown category: {category}"
            raise ValueError(msg)

        current_page = getattr(self, str(config["state_page"]))
        skip = self.limit * (current_page - 1)

        self.is_loading = True
        yield None

        all_results: list[AnyPreviewModel] = []
        total = 0

        try:
            for ref_field in config["reference_fields"]:
                response = connector.fetch_preview_items(
                    query_string=None,
                    entity_type=[str(config["entity_type"])],
                    skip=skip,
                    limit=self.limit,
                    reference_field=ref_field,
                    referenced_identifier=[str(self.merged_login_person.identifier)],
                )
                all_results.extend(response.items)
                total += response.total

        except HTTPError as exc:
            self.is_loading = False
            setattr(self, str(config["state_page"]), 1)
            setattr(self, str(config["state_total"]), 0)
            setattr(self, str(config["state_list"]), [])
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
            return

        self.is_loading = False
        transformed_results = transform_models_to_results(all_results)
        transformed_results = add_external_links_to_results(transformed_results)

        setattr(self, str(config["state_list"]), transformed_results)
        setattr(self, str(config["state_total"]), total)

    @rx.event
    def get_consent(self) -> Generator[EventSpec | None]:
        """Fetch the user's consent status."""
        if not self.merged_login_person:
            yield None
            return

        connector = BackendApiConnector.get()
        try:
            response = connector.fetch_preview_items(
                query_string=None,
                entity_type=["MergedConsent"],
                referenced_identifier=[str(self.merged_login_person.identifier)],
                reference_field="hasDataSubject",
            )
        except HTTPError as exc:
            self.is_loading = False
            yield None
            yield from escalate_error(
                "backend", "No Consent could be fetched.", exc.response.text
            )
        else:
            if response.total > 0:
                self.consent_status = transform_models_to_results([response.items[0]])[
                    0
                ]
            else:
                self.consent_status = None

    @rx.event
    def submit_rule_set(
        self,
        consented: str,
    ) -> Generator[EventSpec | None]:
        """Convert the fields to a rule set and submit it to the backend."""
        if not self.merged_login_person:
            yield None
            return

        is_consenting = consented == "consent"

        additive_consent = AdditiveConsent(
            hasConsentStatus=(
                ConsentStatus["VALID_FOR_PROCESSING"]
                if is_consenting
                else ConsentStatus["INVALID_FOR_PROCESSING"]
            ),
            hasDataSubject=self.merged_login_person.identifier,
            isIndicatedAtTime=YearMonthDayTime(
                datetime.now(tz=ZoneInfo("Europe/Berlin")).isoformat()
            ),
            hasConsentType=(
                ConsentType["EXPRESSED_CONSENT"] if is_consenting else None
            ),
        )

        rule_set_request = ConsentRuleSetRequest(additive=additive_consent)
        try:
            self._send_rule_set_request(rule_set_request)
        except HTTPError as exc:
            self.reset()  # type: ignore[no-untyped-call]
            yield from escalate_error(
                "backend", "error submitting rule set", exc.response.text
            )
            return
        else:
            yield type(self).get_consent()  # type: ignore[operator]
            yield type(self).show_submit_success_toast()  # type: ignore[operator]

    def _send_rule_set_request(self, rule_set: AnyRuleSetRequest) -> AnyRuleSetResponse:
        """Send the rule set to the backend."""
        connector = BackendApiConnector.get()
        if self.consent_status:
            return connector.update_rule_set(self.consent_status.identifier, rule_set)
        return connector.create_rule_set(rule_set)

    @rx.event
    def show_submit_success_toast(self) -> EventSpec:
        """Show a toast for a successfully submitted rule-set."""
        return cast(
            "EventSpec",
            rx.toast.success(
                title=self.label_save_success_dialog_title,
                description=self.label_save_success_dialog_content,
                class_name="editor-toast",
                close_button=True,
                dismissible=True,
                duration=5000,
            ),
        )

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human-readable display values."""
        for result_list in (
            self.user_projects,
            self.user_resources,
            self.user_publications,
        ):
            for result in result_list:
                for preview in result.preview:
                    if preview.identifier and not preview.text:
                        async with self:
                            await resolve_editor_value(preview)

    @label_var(
        label_id="consent.consent_status.consented_format", deps=["consent_datetime"]
    )
    def label_consent_status_consented_format(self) -> list[str]:
        """Label for consent.consent_status.consented_format."""
        return [self.consent_datetime]

    @label_var(
        label_id="consent.consent_status.declined_format", deps=["consent_datetime"]
    )
    def label_consent_status_declined_format(self) -> list[str]:
        """Label for consent.consent_status.declined_format."""
        return [self.consent_datetime]

    @label_var(label_id="consent.consent_status.no_consent")
    def label_consent_status_no_consent(self) -> None:
        """Label for consent.status.no_consent."""

    @label_var(label_id="consent.resources.title")
    def label_resources_title(self) -> None:
        """Label for resources.title."""

    @label_var(label_id="consent.projects.title")
    def label_projects_title(self) -> None:
        """Label for projects.title."""

    @label_var(label_id="consent.publications.title")
    def label_publications_title(self) -> None:
        """Label for publications.title."""

    @label_var(label_id="consent.user_data.loading")
    def label_user_data_loading(self) -> None:
        """Label for user_data.loading  ."""

    @label_var(label_id="consent.consent_box.consent_button")
    def label_consent_box_consent_button(self) -> None:
        """Label for consent_box.consent_button."""

    @label_var(label_id="consent.consent_box.no_consent_button")
    def label_consent_box_no_consent_button(self) -> None:
        """Label for consent_box.no_consent_button."""

    @label_var(label_id="consent.consent_status.loading")
    def label_consent_status_loading(self) -> None:
        """Label for consent_status.loading."""

    @label_var(label_id="consent.save_success_dialog.title")
    def label_save_success_dialog_title(self) -> None:
        """Label for save_success_dialog.title."""

    @label_var(label_id="consent.save_success_dialog.content")
    def label_save_success_dialog_content(self) -> None:
        """Label for save_success_dialog.content."""

    @label_var(label_id="consent.nav_bar.consent_navitem")
    def label_nav_bar_consent_navitem(self) -> None:
        """Label for nav_bar.consent_navitem."""
