from collections.abc import Generator
from typing import Annotated

import reflex as rx
from pydantic import Field
from reflex.event import EventSpec
from requests import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity import get_provider
from mex.common.ldap.connector import LDAPConnector
from mex.common.models import MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
from mex.common.models.person import FullNameStr, OrcidIdStr
from mex.common.types import Email
from mex.editor.exceptions import escalate_error
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
    current_page: Annotated[int, Field(ge=1)] = 1
    limit: Annotated[int, Field(ge=1, le=100)] = 10
    is_loading: bool = True

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
            self.is_loading = False
        return None

    @rx.var(cache=False)
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

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

    @rx.event(background=True)
    async def resolve_identifiers(self) -> None:
        """Resolve identifiers to human readable display values."""
        for result in self.user_projects:
            for preview in result.preview:
                if preview.identifier and not preview.text:
                    async with self:
                        await resolve_editor_value(preview)
