import reflex as rx
from reflex.event import EventSpec


class User(rx.Base):
    """Info on the currently logged-in user."""

    name: str
    authorization: str
    write_access: bool


class State(rx.State):
    """The base state for the app."""

    user: User | None = None

    def logout(self, _) -> EventSpec:
        """Log out a user."""
        self.reset()
        return rx.redirect("/")

    def check_login(self) -> EventSpec | None:
        """Check if a user is logged in."""
        if not self.logged_in:
            return rx.redirect("/login")
        return None

    @rx.var
    def logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self.user is not None
