from typing import TypedDict

import reflex as rx


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


class ReferenceFieldParameters(TypedDict):
    """Reference field parameters to pass to the backend connector."""

    reference_field: str | None
    referenced_identifier: list[str] | None
