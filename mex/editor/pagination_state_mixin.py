import math
from typing import TYPE_CHECKING

import reflex as rx

if TYPE_CHECKING:
    from pydantic.v1.fields import ModelField


class PaginationStateMixin(rx.State, mixin=True):
    """State-Mixin for pagination behaviour."""

    total: int = 0
    limit: int = 50
    current_page: int = 1

    @rx.var
    def max_page(self) -> int:
        """Return the maximum page, based on total and limit."""
        return math.ceil(self.total / self.limit)

    @rx.var
    def skip(self) -> int:
        """Return the skip/offset, based on limit and current_page."""
        return self.limit * (self.current_page - 1)

    @rx.var
    def page_selection(self) -> list[str]:
        """Return a list of total pages based on the number of results."""
        return [f"{i + 1}" for i in range(self.max_page)]

    @rx.var
    def disable_page_selection(self) -> bool:
        """Whether the page selection in the pagination should be disabled."""
        return self.current_page >= self.max_page

    @rx.var
    def disable_previous_page(self) -> bool:
        """Disable the 'Previous' button if on the first page."""
        return self.current_page <= 1

    @rx.var
    def disable_next_page(self) -> bool:
        """Disable the 'Next' button if on the last page."""
        return self.current_page >= self.max_page

    @rx.event
    def set_total(self, total: int) -> None:
        """Set the total of the pagination."""
        self.total = total
        self.set_current_page(self.current_page)  # type: ignore[operator]

    @rx.event
    def set_current_page(self, page_number: str | int) -> None:
        """Set the current page (coerced to be between 1 and max_page)."""
        page_number = int(page_number) if page_number else 1
        self.current_page = max(min(page_number, self.max_page), 1)

    @rx.event
    def go_to_first_page(self) -> None:
        """Navigate to the first page."""
        self.current_page = 1

    @rx.event
    def go_to_previous_page(self) -> None:
        """Navigate to the previous page."""
        self.set_current_page(self.current_page - 1)  # type: ignore[operator]

    @rx.event
    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        self.set_current_page(self.current_page + 1)  # type: ignore[operator]

    @rx.event
    def reset_pagination(self) -> None:
        """Reset the pagination to its default values."""
        fields: dict[str, ModelField] = self.get_fields()
        self.total = 0
        self.current_page = 1
        self.limit = fields["limit"].default
