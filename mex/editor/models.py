from importlib.resources import files
from typing import Literal

import reflex as rx
import yaml
from pydantic import TypeAdapter

from mex.common.models import BaseModel


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
    authorization: str
    write_access: bool


class NavItem(rx.Base):
    """Model for one navigation bar item."""

    title: str = ""
    path: str = "/"
    raw_path: str = "/"
    underline: Literal["always", "none"] = "none"


class ModelConfig(BaseModel):
    """Configuration for how to display an entity type in the frontend."""

    title: str
    preview: list[str] = []
    icon: str


MODEL_CONFIG_BY_STEM_TYPE = TypeAdapter(dict[str, ModelConfig]).validate_python(
    yaml.safe_load(files("mex.editor").joinpath("models.yaml").open())
)
