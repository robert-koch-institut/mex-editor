import reflex as rx

from mex.common.types import MergedPrimarySourceIdentifier
from mex.editor.models import EditorValue


class InputConfig(rx.Base):
    """Model for configuring input masks."""

    badge_options: list[str] = []
    editable_href: bool = False
    editable_badge: bool = False
    editable_text: bool = False


class EditorPrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: EditorValue
    identifier: MergedPrimarySourceIdentifier
    input_config: InputConfig | None
    editor_values: list[EditorValue] = []
    enabled: bool


class EditorField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditorPrimarySource] = []
