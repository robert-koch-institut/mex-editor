from collections.abc import Sequence
from dataclasses import dataclass
from importlib.resources import files
from typing import Protocol

import reflex as rx
import yaml
from pydantic import TypeAdapter
from reflex.event import EventType
from reflex.vars import Var

from mex.common.models import BaseModel
from mex.common.types import MergedPersonIdentifier
from mex.editor.pagination_state_mixin import PaginationStateMixin


class EqualityDetector(Protocol):
    """Interface for checking equality without overriding __eq__."""

    def is_equal(self, other: "EqualityDetector") -> bool: ...  # noqa: D102


def sequence_is_equal(
    left: Sequence[EqualityDetector], right: Sequence[EqualityDetector]
) -> bool:
    """Check if the given sequences are equal (based on EqualityDetector.is_equal)."""
    try:
        return all(a.is_equal(b) for a, b in zip(left, right, strict=True))
    except ValueError:
        return False  # sequences don't have same length


class EditorValue(rx.Base):
    """Model for describing atomic values in the editor."""

    text: str | None = None
    identifier: str | None = None
    badge: str | None = None
    href: str | None = None
    external: bool = False
    enabled: bool = True
    being_edited: bool = False

    def is_equal(self, other: "EqualityDetector") -> bool:
        """Check if self and other are equal."""
        if isinstance(other, EditorValue):
            exclude = {"text"} if other.identifier and not other.text else set()
            self_dict = self.dict(exclude=exclude)
            other_dict = other.dict(exclude=exclude)
            return self_dict == other_dict
        return False


class User(rx.Base):
    """Info on the currently logged-in user."""

    name: str
    write_access: bool


class MergedLoginPerson(rx.Base):
    """Info on the currently logged-in user from the merged login endpoint."""

    identifier: MergedPersonIdentifier | None = None
    full_name: list[str] | None = None
    email: list[str] | None = None
    orcid_id: list[str] | None = None


class NavItem(rx.Base):
    """Model for one navigation bar item."""

    title: str = ""
    path: str = "/"
    raw_path: str = "/"
    underline: str = "none"


class ModelConfig(BaseModel):
    """Configuration for how to display an entity type in the frontend."""

    title: str
    preview: list[str] = []
    textarea: list[str] = []


MODEL_CONFIG_BY_STEM_TYPE = TypeAdapter(dict[str, ModelConfig]).validate_python(
    yaml.safe_load(files("mex.editor").joinpath("models.yaml").open())
)
LANGUAGE_VALUE_NONE = "None"


@dataclass
class PaginationButtonOptions:
    """Options for a pagination button."""

    disabled: bool | Var[bool]
    on_click: EventType[()] | None = None


@dataclass
class PaginationPageOptions:
    """Options for the pagination component."""

    current_page: int | Var[int]
    pages: list[str] | Var[list[str]]
    disabled: bool | Var[bool]
    on_change: EventType[()] | None = None


@dataclass
class PaginationOptions:
    """Options for the pagination component."""

    prev_options: PaginationButtonOptions
    next_options: PaginationButtonOptions
    page_options: PaginationPageOptions

    @staticmethod
    def create(
        state: PaginationStateMixin | type[PaginationStateMixin],
        on_page_change: EventType[()] | None = None,
    ) -> "PaginationOptions":
        """Create pagination options for a given state.

        Args:
            state: The state to create the options for.
            on_page_change: EventHandler that gets executed when the current_page
            changes. Defaults to None.
        """
        prev_click = (
            [state.go_to_previous_page, on_page_change]
            if on_page_change
            else [state.go_to_previous_page]
        )
        next_click = (
            [state.go_to_next_page, on_page_change]
            if on_page_change
            else [state.go_to_next_page]
        )
        change_page = (
            [state.set_current_page, on_page_change]
            if on_page_change
            else [state.set_current_page]
        )

        return PaginationOptions(
            PaginationButtonOptions(state.disable_previous_page, prev_click),
            PaginationButtonOptions(state.disable_next_page, next_click),
            PaginationPageOptions(
                state.current_page,
                state.page_selection,
                state.disable_page_selection,
                change_page,
            ),
        )
