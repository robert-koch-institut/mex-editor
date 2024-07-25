from typing import cast

from pydantic import SecretStr

from mex.common.models import BaseModel


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
