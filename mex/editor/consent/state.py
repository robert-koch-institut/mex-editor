import math
from collections.abc import Generator
from typing import Annotated

import reflex as rx
from pydantic import Field, ValidationError
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity import get_provider
from mex.common.ldap.connector import LDAPConnector
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
from mex.common.models.person import FullNameStr, OrcidIdStr
from mex.common.types import Email
from mex.editor.exceptions import escalate_error
from mex.editor.models import NavItem
from mex.editor.rules.models import EditorField
from mex.editor.rules.transform import (
    transform_fields_to_rule_set,
    transform_validation_error_to_messages,
)
from mex.editor.search.models import SearchResult
from mex.editor.search.transform import transform_models_to_results
from mex.editor.state import State
from mex.editor.utils import resolve_editor_value


class ConsentState(State):
    """State for the consent component."""

    display_name: str | list[FullNameStr] | None = None
    user_mail: list[Email] = []
    user_orcidID: list[OrcidIdStr] = []
    user_projects: list[SearchResult] = []
    user_resources: list[SearchResult] = []
    user_bib_resources: list[SearchResult] = []
    total: Annotated[int, Field(ge=0)] = 0
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 10
    is_loading: bool = True
    consent_nav_items: list[NavItem] = [
        NavItem(
            title="Consent",
            path="/consent",
            raw_path="/consent/",
        )
    ]

    @rx.event
    def load_user(self) -> EventSpec | Generator[EventSpec | None, None, None]:
        """Set the stem type to a default."""
        ldap_connector = LDAPConnector.get()
        if not self.user_ldap:
            self.target_path_after_login = self.router.page.raw_path
            return rx.redirect("/login-ldap")
        self.is_loading = True
        ldap_person = ldap_connector.get_person(sAMAccountName=self.user_ldap.name)
        self.display_name = ldap_person.displayName
        provider = get_provider()
        primary_source_identities = provider.fetch(
            had_primary_source=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
            identifier_in_primary_source="ldap",
        )
        try:
            identities = provider.fetch(
                identifier_in_primary_source=str(ldap_person.objectGUID),
                had_primary_source=primary_source_identities[0].stableTargetId,  # type: ignore  [arg-type]
            )
        except HTTPError as exc:
            self.is_loading = False
            yield None
            yield from escalate_error(
                "backend", "error fetching identity", exc.response.text
            )
        else:
            connector = BackendApiConnector.get()
            if len(identities) > 0:
                person = connector.get_merged_item(identities[0].stableTargetId)
                self.display_name = person.fullName  # type: ignore [union-attr]
                self.user_mail = person.email  # type: ignore [union-attr]
                self.user_orcidID = person.orcidId  # type: ignore [union-attr]
                self._update_raw_path(
                    self.consent_nav_items[0], identifier=str(person.identifier)
                )
            self.is_loading = False
        return None

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
        self.set_page(self.current_page - 1)

    @rx.event
    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        self.set_page(self.current_page + 1)

    @rx.event
    def set_page(self, page_number: str | int) -> None:
        """Set the current page and refresh the results."""
        self.current_page = int(page_number)

    @rx.event
    def get_all_data(self) -> Generator[EventSpec | None, None, None]:
        """Fetch all data for the user."""
        yield from self.get_projects()
        yield from self.get_resources()
        yield from self.get_bibliography()

    @rx.event
    def get_bibliography(self) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's bibliography."""
        yield from self.fetch_data("MergedBibliographicResource")

    @rx.event
    def get_resources(self) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's resources."""
        yield from self.fetch_data("MergedResource")

    @rx.event
    def get_projects(self) -> Generator[EventSpec | None, None, None]:
        """Fetch the user's activities."""
        yield from self.fetch_data("MergedActivity")

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
                had_primary_source=None,
                skip=skip,
                limit=self.limit,
            )
        except HTTPError as exc:
            self.is_loading = False
            self.current_page = 1
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
            elif entity_type == "MergedBibliographicResource":
                self.user_bib_resources = transform_models_to_results(response.items)
            self.total += response.total

    @rx.event
    def submit_rule_set(self) -> Generator[EventSpec | None, None, None]:
        """Convert the fields to a rule set and submit it to the backend."""
        fields = [
            EditorField(name="hasConsentStatus", is_required=True),
            EditorField(name="hasDataSubject", is_required=True),
        ]
        try:
            rule_set_request = transform_fields_to_rule_set("Consent", fields)
        except ValidationError as exc:
            self.validation_messages = transform_validation_error_to_messages(exc)
            return
        try:
            self._send_rule_set_request(rule_set_request)
        except HTTPError as exc:
            self.reset()
            yield from escalate_error(
                "backend", "error submitting rule set", exc.response.text
            )
            return
        else:
            yield self.show_submit_success_toast()

    @rx.event
    def set_text_value(self, field_name: str, index: int, value: str) -> None:
        """Set the text attribute on an additive editor value."""
        primary_source = self._get_editable_primary_source_by_field_name(field_name)
        primary_source.editor_values[index].text = value

    def _send_rule_set_request(self, rule_set: AnyRuleSetRequest) -> AnyRuleSetResponse:
        """Send the rule set to the backend."""
        connector = BackendApiConnector.get()
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
        """Resolve identifiers to human readable display values."""
        self.get_all_data()
        for result in self.user_projects:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)
