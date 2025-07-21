from dataclasses import dataclass

from mex.editor.models import EditorValue


@dataclass
class IngestResult:
    """Ingest search result."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]
    show_properties: bool
    all_properties: list[EditorValue]
    show_ingest_button: bool
