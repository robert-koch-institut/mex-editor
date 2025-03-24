from typing import cast

from pydantic import SecretStr

from mex.common.fields import ALL_MODEL_CLASSES_BY_NAME
from mex.common.models import BaseModel
from mex.common.types import (
    AnyNestedModel,
    AnyPrimitiveType,
    AnyTemporalEntity,
    AnyVocabularyEnum,
)
from mex.common.utils import get_all_fields, get_inner_types

AnyModelValue = (
    AnyNestedModel | AnyPrimitiveType | AnyTemporalEntity | AnyVocabularyEnum
)

TYPES_BY_FIELDS_BY_CLASS_NAMES = {
    class_name: {
        field_name: list(get_inner_types(model_class))
        for field_name in get_all_fields(model_class)
    }
    for class_name, model_class in ALL_MODEL_CLASSES_BY_NAME.items()
}


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
