from importlib.resources import files
from typing import cast

import yaml
from pydantic import BaseModel, SecretStr, TypeAdapter

from mex.common.models import BaseModel

DEFAULT_MODEL_CONFIG_PATH = files("mex.editor").joinpath("models.yaml")
ModelConfigByStemType = dict[str, "ModelConfig"]


class EditorUserPassword(SecretStr):
    """An editor password used for basic authentication along with a username."""


class EditorUserDatabase(BaseModel):
    """Database containing usernames and passwords for the editor users."""

    read: dict[str, EditorUserPassword] = {}
    write: dict[str, EditorUserPassword] = {}

    def __getitem__(
        self, key: str
    ) -> dict[str, EditorUserPassword]:  # stop-gap: MX-1596
        """Return an attribute in indexing syntax."""
        return cast(dict[str, EditorUserPassword], getattr(self, key))


class ModelConfig(BaseModel):
    """Configuration for how to display an entity type in the frontend."""

    title: str
    preview: list[str] = []

    @classmethod
    def load_all(cls) -> ModelConfigByStemType:
        """Load the full model config and group items by stem type."""
        return TypeAdapter(ModelConfigByStemType).validate_python(
            yaml.safe_load(open(DEFAULT_MODEL_CONFIG_PATH.open().read()))
        )
