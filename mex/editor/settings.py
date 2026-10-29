from pathlib import Path
from typing import Literal

from pydantic import Field

from mex.common.settings import BaseSettings


class EditorSettings(BaseSettings):
    """Settings for the editor application."""

    host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the server will run on.",
        validation_alias="MEX_EDITOR__HOST",
    )
    port: int = Field(
        8000,
        gt=0,
        lt=65536,
        description="Port that the server should listen on.",
        validation_alias="MEX_EDITOR__PORT",
    )
    base_href: Literal["/", "/editor/"] = Field(
        "/",
        validation_alias="MEX_EDITOR__BASE_HREF",
    )
    cors_allowed_origins: list[str] = Field(
        [],
        description=(
            "Origins that browsers may call the editor api from, e.g. "
            '`["https://admin.example.org"]`. Empty means same-origin only.'
        ),
        validation_alias="MEX_EDITOR__CORS_ALLOWED_ORIGINS",
    )
    client_dir: Path = Field(
        Path(__file__).parent.resolve() / "client" / "dist",
        validation_alias="MEX_EDITOR__CLIENT_DIR",
    )
