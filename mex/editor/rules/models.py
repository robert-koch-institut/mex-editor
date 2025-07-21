from dataclasses import dataclass

from mex.common.types import MergedPrimarySourceIdentifier
from mex.editor.models import EditorValue


@dataclass
class InputConfig:
    """Model for configuring input masks."""

    badge_default: str | None  # value to pre-select in drop-down menu
    badge_options: list[str]  # possible values to show in drop-down menu
    badge_titles: list[str]  # title for the collection of drop-drown choices
    editable_href: bool  # whether the href attribute is editable as text
    editable_badge: bool  # whether the badge is editable as a drop-down
    editable_identifier: bool  # whether the identifier is editable as text
    editable_text: bool  # whether the text is editable as plain text
    allow_additive: bool  # whether this field belongs to an additive rule


@dataclass
class ValidationMessage:
    """Model for describing validation errors."""

    field_name: str
    message: str
    input: str


@dataclass
class EditorPrimarySource:
    """Model for describing the editor state for one primary source."""

    name: EditorValue
    identifier: MergedPrimarySourceIdentifier
    input_config: InputConfig
    editor_values: list[EditorValue]
    enabled: bool


@dataclass
class EditorField:
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditorPrimarySource]
    is_required: bool
