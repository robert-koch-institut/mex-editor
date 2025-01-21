import reflex as rx

from mex.editor.models import FixedValue


class AuxResult(rx.Base):
    """Auxiliary search result."""

    identifier: str
    title: list[FixedValue]
    preview: list[FixedValue]
    show_properties: bool
    all_properties: list[FixedValue]
