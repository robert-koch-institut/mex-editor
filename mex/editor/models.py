from importlib.resources import files

import reflex as rx
import yaml
from pydantic import TypeAdapter

from mex.common.models import BaseModel
from mex.common.types import MergedPersonIdentifier


class EditorValue(rx.Base):
    """Model for describing atomic values in the editor."""

    text: str | None = None
    identifier: str | None = None
    badge: str | None = None
    href: str | None = None
    external: bool = False
    enabled: bool = True
    being_edited: bool = False


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
