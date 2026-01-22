from enum import StrEnum

from mex.editor.models import SearchResult


class AuxProvider(StrEnum):
    """Allowed auxiliary providers."""

    LDAP = "ldap"
    ORCID = "orcid"
    WIKIDATA = "wikidata"


ALL_AUX_PROVIDERS: list[AuxProvider] = [
    AuxProvider.LDAP,
    AuxProvider.ORCID,
    AuxProvider.WIKIDATA,
]


class IngestResult(SearchResult):
    """Ingest search result."""

    show_ingest_button: bool
