import reflex as rx

from mex.editor.models import FixedValue


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    title: list[FixedValue]
    preview: list[FixedValue]
