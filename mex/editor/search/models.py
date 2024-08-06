import reflex as rx


class SearchResult(rx.Base):
    """Search result preview."""

    identifier: str
    title: str
    preview: str
