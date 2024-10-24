import reflex as rx


class EditablePrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: str
    editable_values: list[str]


class EditableField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditablePrimarySource]
