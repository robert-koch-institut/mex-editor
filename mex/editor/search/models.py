import reflex as rx

from mex.editor.models import EditorValue


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    stem_type: str
    title: list[EditorValue]
    preview: list[EditorValue]


class ReferenceDialogSearchResult(SearchResult):
    """Search result preview with all properties."""

    all_properties: list[EditorValue]


class SearchPrimarySource(rx.Base):
    """Primary source filter."""

    identifier: str
    title: str
    checked: bool


class ReferenceFieldIdentifierFilter(rx.Base):
    """Reference field identifier for value and validation msg."""

    value: str
    validation_msg: str | None


class ReferenceFieldFilter(rx.Base):
    """Reference field filter."""

    identifiers: list[ReferenceFieldIdentifierFilter]
    field: str
