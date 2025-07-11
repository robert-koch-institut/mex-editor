from typing import Final, Literal

import reflex as rx

from mex.editor.models import EditorValue

AuxProvider = Literal["ldap", "orcid", "wikidata"]

AUX_PROVIDER_LDAP: Final = "ldap"
AUX_PROVIDER_ORDIC: Final = "orcid"
AUX_PROVIDER_WIKIDATA: Final = "wikidata"

AUX_PROVIDERS: list[AuxProvider] = [
    AUX_PROVIDER_LDAP,
    AUX_PROVIDER_ORDIC,
    AUX_PROVIDER_WIKIDATA,
]


class IngestResult(rx.Base):
    """Ingest search result."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]
    show_properties: bool
    all_properties: list[EditorValue]
    show_ingest_button: bool
