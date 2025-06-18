import reflex as rx

from mex.editor.models import EditorValue


class IngestResult(rx.Base):
    """Ingest search result."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]
    show_properties: bool
    all_properties: list[EditorValue]
    show_ingest_button: bool


class IngestNavItem(rx.Base):
    """Model for one ingest navigation bar item."""

    title: str = ""
    value: str = "/"
