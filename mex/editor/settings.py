
from pydantic import Field

from mex.common.settings import BaseSettings
from mex.editor.types import EditorUserDatabase, ModelConfig, ModelConfigByStemType


class EditorSettings(BaseSettings):
    """Settings definition for the editor service."""

    editor_user_database: EditorUserDatabase = Field(
        EditorUserDatabase(),
        description="Database of users.",
        validation_alias="MEX_BACKEND_API_USER_DATABASE",
    )
    model_configs: ModelConfigByStemType = Field(
        default_factory=ModelConfig.load_all,
    )
