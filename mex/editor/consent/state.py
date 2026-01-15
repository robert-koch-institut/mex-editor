import math
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import reflex as rx
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    AdditiveConsent,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
    ConsentRuleSetRequest,
)
from mex.common.types import (
    ConsentStatus,
    ConsentType,
    YearMonthDayTime,
)
from mex.editor.exceptions import escalate_error
from mex.editor.label_var import label_var
from mex.editor.models import NavItem, SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class ConsentState(State):
    """State for the consent component."""

    user_projects: list[SearchResult] = []
    user_resources: list[SearchResult] = []
    consent_status: SearchResult | None = None
    limit: Annotated[int, Field(ge=1, le=100)] = 5
    projects_total: Annotated[int, Field(ge=0)] = 0
    projects_current_page: Annotated[int, Field(ge=1)] = 1
    resources_total: Annotated[int, Field(ge=0)] = 0
    resources_current_page: Annotated[int, Field(ge=1)] = 1
    is_loading: bool = True

    _consent_nav_items: list[NavItem] = [
        NavItem(
            title="consent.nav_bar.consent_navitem",
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

    @rx.var(cache=False)
    def projects_total_pages(self) -> list[str]:
        """Return a list of total pages for projects based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.projects_total / self.limit))]

    @rx.var(cache=False)
    def resources_total_pages(self) -> list[str]:
        """Return a list of total pages for resources based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.resources_total / self.limit))]

    @rx.event
    def get_all_data(self) -> Generator[EventSpec | None, None, None]:
        """Fetch all data for the user."""
        yield type(self).fetch_data("projects")  # type: ignore[operator]
        yield type(self).fetch_data("resources")  # type: ignore[operator]

    @rx.event
    def scroll_to_top(self) -> Generator[EventSpec | None, None, None]:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.event
    def fetch_data(self, category: str) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's projects, resources, or bibliography."""
        connector = BackendApiConnector.get()

        is_projects = category == "projects"
        current_page = (
            self.projects_current_page if is_projects else self.resources_current_page
        )
        entity_type = "MergedActivity" if is_projects else "MergedResource"

        skip = self.limit * (current_page - 1)
        self.is_loading = True
        yield None
        try:
            response = connector.fetch_preview_items(
                query_string=None,
                entity_type=[entity_type],
                skip=skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            if is_projects:
                self.projects_current_page = 1
                self.projects_total = 0
                self.user_projects = []
            else:
                self.resources_current_page = 1
                self.resources_total = 0
                self.user_resources = []
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            transformed_results = transform_models_to_results(response.items)
            if is_projects:
                self.user_projects = transformed_results
                self.projects_total = response.total
            else:
                self.user_resources = transformed_results
                self.resources_total = response.total

    @rx.event
    def get_consent(self) -> Generator[EventSpec | None, None, None]:
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
    ) -> Generator[EventSpec | None, None, None]:
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
            isIndicatedAtTime=YearMonthDayTime(datetime.now(tz=UTC).isoformat()),
            hasConsentType=(
                ConsentType["EXPRESSED_CONSENT"] if is_consenting else None
            ),
        )

        rule_set_request = ConsentRuleSetRequest(additive=additive_consent)
        try:
            self._send_rule_set_request(rule_set_request)
        except HTTPError as exc:
            self.reset()
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
        return rx.toast.success(
            title=self.label_save_success_dialog_title,
            description=self.label_save_success_dialog_content,
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )

    @rx.event(background=True)  # type: ignore[operator]
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human-readable display values."""
        for result_list in (
            self.user_projects,
            self.user_resources,
        ):
            for result in result_list:
                for preview in result.preview:
                    if preview.identifier and not preview.text:
                        async with self:
                            await resolve_editor_value(preview)

    @label_var(label_id="consent.resources.title")
    def label_resources_title(self) -> None:
        """Label for resources.title."""

    @label_var(label_id="consent.projects.title")
    def label_projects_title(self) -> None:
        """Label for projects.title."""

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
