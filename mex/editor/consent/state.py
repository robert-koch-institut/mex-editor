import math
from collections.abc import Generator
from datetime import UTC, datetime
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
from mex.editor.models import NavItem
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class ConsentState(State):
    """State for the consent component."""

    user_projects: list[SearchResult] = []
    user_resources: list[SearchResult] = []
    consent_status: SearchResult | None = None
    total: Annotated[int, Field(ge=0)] = 0
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 10
    is_loading: bool = True

    @staticmethod
    def get_consent_nav_items() -> list[NavItem]:
        """Return navigation items for the consent interface."""
        return [
            NavItem(
                title="Informed Consent",
                path="/consent",
                raw_path="/consent/",
            ),
        ]

    @rx.event
    def load_user(self) -> Generator[EventSpec | None, None, None]:
        """Check the login and get user information."""
        if not self.user_ldap:
            self.target_path_after_login = self.router.page.raw_path
            yield rx.redirect("/login-ldap")
            return
        if self.merged_login_person:
            yield from self.get_consent()  # type: ignore[misc]
        self.is_loading = False

    @rx.var(cache=False)
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var(cache=False)
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        max_page = math.ceil(self.total / self.limit)
        return self.current_page >= max_page

    @rx.event
    def go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        self.current_page = self.current_page - 1

    @rx.event
    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        self.current_page = self.current_page + 1

    @rx.event
    def set_page(self, page_number: str | int) -> None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)

    @rx.event
    def get_all_data(self) -> Generator[EventSpec | None, None, None]:
        """Fetch all data for the user."""
        yield from self.get_projects()  # type: ignore[misc]
        yield from self.get_resources()  # type: ignore[misc]

    @rx.event
    def get_resources(self) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's resources."""
        yield from self.fetch_data("MergedResource")  # type: ignore[misc]

    @rx.event
    def get_projects(self) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's activities."""
        yield from self.fetch_data("MergedActivity")  # type: ignore[misc]

    @rx.event
    def scroll_to_top(self) -> Generator[EventSpec | None, None, None]:
        """Scroll the page to the top."""
        yield rx.call_script("window.scrollTo({top: 0, behavior: 'smooth'});")

    @rx.var(cache=False)
    def total_pages(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(math.ceil(self.total / self.limit))]

    @rx.event
    def fetch_data(self, entity_type: str) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's projects, resources, or bibliography."""
        connector = BackendApiConnector.get()
        skip = self.limit * (self.current_page - 1)
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
            self.current_page = 1
            self.total = 0
            self.user_projects = []
            self.user_resources = []
            yield None
            yield from escalate_error(
                "backend", "error fetching merged items", exc.response.text
            )
        else:
            self.is_loading = False
            if entity_type == "MergedActivity":
                self.user_projects = transform_models_to_results(response.items)
            elif entity_type == "MergedResource":
                self.user_resources = transform_models_to_results(response.items)
            self.total = response.total

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
            yield from self.get_consent()  # type: ignore[misc]
            yield self.show_submit_success_toast()  # type: ignore[misc]

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
            title="Saved",
            description="Consent was saved successfully.",
            class_name="editor-toast",
            close_button=True,
            dismissible=True,
            duration=5000,
        )

    @rx.event(background=True)
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
