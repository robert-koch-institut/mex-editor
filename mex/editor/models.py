from collections.abc import Sequence
from importlib.resources import files
from typing import Protocol

import reflex as rx
import yaml
from pydantic import TypeAdapter

from mex.common.models import BaseModel
from mex.common.types import MergedPersonIdentifier


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
