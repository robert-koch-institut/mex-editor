import reflex as rx

from mex.common.types import MergedPrimarySourceIdentifier
from mex.editor.models import EditorValue


class InputConfig(rx.Base):
    """Model for configuring input masks."""

    badge_default: str | None = None  # value to pre-select in drop-down menu
    badge_options: list[str] = []  # possible values to show in drop-down menu
    badge_titles: list[str] = []  # title explaining the drop-drown choice
    editable_href: bool = False  # whether the href attribute is editable as text
    editable_badge: bool = False  # whether the badge is editable as a drop-down
    editable_text: bool = False  # whether the text is editable as plain text
    allow_additive: bool = False  # whether this field belongs to an additive rule


class EditorPrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: EditorValue
    identifier: MergedPrimarySourceIdentifier
    input_config: InputConfig
    editor_values: list[EditorValue] = []
    enabled: bool = True


class EditorField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditorPrimarySource] = []
