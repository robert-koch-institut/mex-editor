import reflex as rx

from mex.editor.models import EditorValue


class AuxResult(rx.Base):
    """Auxiliary search result."""

    identifier: str
    title: list[EditorValue]
    preview: list[EditorValue]
    show_properties: bool
    all_properties: list[EditorValue]
    show_import_button: bool
