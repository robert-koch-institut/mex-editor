import reflex as rx


class FixedValue(rx.Base):
    """Model for describing fixed values that are not editable."""

    text: str | None
    language: str | None
    href: str | None
    tooltip: str | None
    external: bool


class EditablePrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: FixedValue
    values: list[FixedValue]


class EditableField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    primary_sources: list[EditablePrimarySource]
