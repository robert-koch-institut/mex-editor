import reflex as rx

from mex.common.types import MergedPrimarySourceIdentifier
from mex.editor.models import EditorValue


class InputConfig(rx.Base):
    """Model for configuring input masks."""

    data_type: str | None = None


class EditorPrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: EditorValue
    identifier: MergedPrimarySourceIdentifier
    editor_values: list[EditorValue] = []
    enabled: bool = True
    input_config: InputConfig | None = None
    additive_values: list[EditorValue] = []


class EditorField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditorPrimarySource] = []
