import reflex as rx

from mex.common.types import MergedPrimarySourceIdentifier
from mex.editor.models import FixedValue


class EditablePrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: FixedValue
    identifier: MergedPrimarySourceIdentifier
    editor_values: list[FixedValue]
    enabled: bool = True


class EditableField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditablePrimarySource]
