from pydantic import Field

from mex.common.settings import BaseSettings
from mex.common.types import IdentityProvider
from mex.editor.types import EditorIdentityProvider, EditorUserDatabase


class EditorSettings(BaseSettings):
    """Settings definition for the editor service."""

    editor_user_database: EditorUserDatabase = Field(
        EditorUserDatabase(),
        description="Database of users.",
        validation_alias="MEX_BACKEND_API_USER_DATABASE",
    )
    identity_provider: IdentityProvider | EditorIdentityProvider = Field(
        IdentityProvider.MEMORY,
        description="Provider to assign stableTargetIds to new model instances.",
        validation_alias="MEX_IDENTITY_PROVIDER",
    )  # type: ignore[assignment]
