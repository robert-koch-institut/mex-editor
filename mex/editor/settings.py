from pydantic import Field

from mex.common.settings import BaseSettings
from mex.editor.types import EditorUserDatabase


class EditorSettings(BaseSettings):
    """Settings definition for the editor service."""

    editor_user_database: EditorUserDatabase = Field(
        EditorUserDatabase(),
        description="Database of users.",
        validation_alias="MEX_BACKEND_API_USER_DATABASE",
    )
