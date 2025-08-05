import reflex as rx

from mex.editor.models import EditorValue


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    stem_type: str
    title: list[EditorValue]
    preview: list[EditorValue]


class SearchPrimarySource(rx.Base):
    """Primary source filter."""

    identifier: str
    title: str
    checked: bool
