from pydantic import Field

from mex.common.settings import BaseSettings
from mex.editor.types import EditorUserDatabase


class EditorSettings(BaseSettings):
    """Settings definition for the editor service."""

    editor_api_host: str = Field(
        "localhost",
        min_length=1,
        max_length=256,
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
    editor_api_root_path: str = Field(
        "",
        description="Root path that the editor api should run under.",
        validation_alias="MEX_EDITOR_API_ROOT_PATH",
    )
    editor_api_deploy_url: str = Field(
        "http://localhost:8031",
        min_length=1,
        max_length=256,
        description="Full URL that users use to reach the editor api.",
        validation_alias="MEX_EDITOR_API_DEPLOY_URL",
    )
    editor_frontend_host: str = Field(
        "localhost",
        min_length=1,
        max_length=256,
        description="Host that the editor frontend will run on.",
        validation_alias="MEX_EDITOR_FRONTEND_HOST",
    )
    editor_frontend_port: int = Field(
        8030,
        gt=0,
        lt=65536,
        description="Port that the editor frontend should serve on.",
        validation_alias="MEX_EDITOR_FRONTEND_PORT",
    )
    editor_frontend_root_path: str = Field(
        "",
        description="Root path that the editor frontend should run under.",
        validation_alias="MEX_EDITOR_FRONTEND_ROOT_PATH",
    )
    editor_frontend_deploy_url: str = Field(
        "https://localhost:8030",
        min_length=1,
        description="Full URL that users use to reach the editor frontend.",
        validation_alias="MEX_EDITOR_FRONTEND_DEPLOY_URL",
    )
    editor_frontend_static_directory: str = Field(
        ".web/_static",
        min_length=1,
        description="Directory containing static files for the frontend.",
        validation_alias="MEX_EDITOR_FRONTEND_STATIC_DIRECTORY",
    )
    editor_user_database: EditorUserDatabase = Field(
        EditorUserDatabase(),
        description="Database of users.",
        validation_alias="MEX_BACKEND_API_USER_DATABASE",
    )
