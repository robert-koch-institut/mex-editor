import reflex as rx

from mex.editor.layout import page


def index() -> rx.Component:
    """Return the index for the merge component."""
    return page(
        rx.section(
            rx.heading(
                "Merge",
                custom_attrs={"data-testid": "merge-heading"},
                style={"margin": "1em 0"},
            ),
            style={"width": "100%"},
            custom_attrs={"data-testid": "merge-section"},
        )
    )
