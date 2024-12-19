import reflex as rx

from mex.editor.models import EditorValue


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]
