from importlib.resources import files
from typing import Literal
from urllib.parse import urlencode

import reflex as rx
import yaml
from pydantic import TypeAdapter

from mex.common.models import BaseModel


class EditorValue(rx.Base):
    """Model for describing atomic values in the editor."""

    text: str | None = None
    badge: str | None = None
    href: str | None = None
    external: bool = False
    enabled: bool = True


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

    def update_raw_path(self, params: dict[str, int | str | list[str]]) -> None:
        """Render the parameters into a raw path."""
        raw_path = self.path
        param_tuples = list(params.items())
        for key, value in param_tuples:
            if f"[{key}]" in raw_path:
                raw_path = raw_path.replace(f"[{key}]", f"{value}")
        query_tuples: list[tuple[str, str]] = []
        for key, value in param_tuples:
            if f"[{key}]" not in self.path:
                value_list = value if isinstance(value, list) else [f"{value}"]
                query_tuples.extend((key, item) for item in value_list if item)
        if query_str := urlencode(query_tuples):
            raw_path = f"{raw_path}?{query_str}"
        self.raw_path = raw_path


class ModelConfig(BaseModel):
    """Configuration for how to display an entity type in the frontend."""

    title: str
    preview: list[str] = []
    icon: str


MODEL_CONFIG_BY_STEM_TYPE = TypeAdapter(dict[str, ModelConfig]).validate_python(
    yaml.safe_load(files("mex.editor").joinpath("models.yaml").open())
)
