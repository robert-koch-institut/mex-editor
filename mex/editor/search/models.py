from dataclasses import dataclass

from mex.editor.models import EditorValue


@dataclass
class SearchResult:
    """Search result preview."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]


@dataclass
class SearchPrimarySource:
    """Primary source filter."""

    identifier: str
    title: str
    checked: bool
