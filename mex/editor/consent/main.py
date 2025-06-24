import reflex as rx

from mex.editor.consent.state import ConsentState


def index() -> rx.Component:
    """Return the index for the consent component."""
    return rx.vstack(
        f"""\
Dear {ConsentState.display_name},
do you give your consent for publishing the following data in MEx?
"""
    )
