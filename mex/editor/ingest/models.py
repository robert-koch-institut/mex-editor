from enum import StrEnum

import reflex as rx

from mex.editor.models import EditorValue


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


class IngestResult(rx.Base):
    """Ingest search result."""

    identifier: str
    stem_type: str
    title: list[EditorValue]
    preview: list[EditorValue]
    show_properties: bool
    all_properties: list[EditorValue]
    show_ingest_button: bool
