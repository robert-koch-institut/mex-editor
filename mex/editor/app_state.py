import reflex as rx


class AppState(rx.State):
    current_locale: str = "de-DE"

    @rx.event
    def change_locale(self, locale: str) -> None:
        """Change the current locale to the given one and reload the page.

        Args:
            locale: The locale to change to.
        """
        self.current_locale = locale
