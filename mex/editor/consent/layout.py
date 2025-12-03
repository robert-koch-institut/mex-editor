import reflex as rx

from mex.editor.consent.state import ConsentState
from mex.editor.layout import page as shared_page


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with the consent navigation bar and given children."""
    return shared_page(
        *children,
        user_type="user_ldap",
        nav_items_source=ConsentState.get_consent_nav_items(),
        include_navigate_dialog=False,
    )
