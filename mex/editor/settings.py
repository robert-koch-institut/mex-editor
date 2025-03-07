from pydantic import Field

from mex.common.settings import BaseSettings
from mex.editor.types import EditorUserDatabase


class EditorSettings(BaseSettings):
    """Settings definition for the editor service."""

    editor_api_host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the editor api will run on.",
        validation_alias="MEX_EDITOR_API_HOST",
    )
    editor_api_port: int = Field(
        8031,
        gt=0,
        lt=65536,
        description="Port that the editor api should listen on.",
        validation_alias="MEX_EDITOR_API_PORT",
    )
    editor_frontend_port: int = Field(
        8030,
        gt=0,
        lt=65536,
        description="Port that the editor frontend should serve on.",
        validation_alias="MEX_EDITOR_FRONTEND_PORT",
    )
    editor_api_root_path: str = Field(
        "",
        description="Root path that the editor server should run under.",
        validation_alias="MEX_EDITOR_API_ROOT_PATH",
    )
    editor_user_database: EditorUserDatabase = Field(
        EditorUserDatabase(),
        description="Database of users.",
        validation_alias="MEX_BACKEND_API_USER_DATABASE",
    )
