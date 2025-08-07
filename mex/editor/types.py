from collections.abc import Generator
from typing import cast

from pydantic import SecretStr
from reflex.event import EventNamespace, EventSpec

from mex.common.models import BaseModel
from mex.common.types import (
    AnyNestedModel,
    AnyPrimitiveType,
    AnyTemporalEntity,
    AnyVocabularyEnum,
)

AnyModelValue = (
    AnyNestedModel | AnyPrimitiveType | AnyTemporalEntity | AnyVocabularyEnum
)
EventGenerator = Generator[EventSpec | EventNamespace | None, None, None]


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
        return cast("dict[str, EditorUserPassword]", getattr(self, key))
