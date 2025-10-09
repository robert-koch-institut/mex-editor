from async_lru import alru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import EmptySearchResultError, MExError
from mex.common.settings import SETTINGS_STORE
from mex.editor.models import EditorValue
from mex.editor.settings import EditorSettings
from mex.editor.transform import transform_models_to_title


@alru_cache(maxsize=5000)
async def resolve_identifier(identifier: str) -> str:
    """Resolve identifiers to human readable display values."""
    # TODO(ND): use proper connector method when available (stop-gap MX-1984)
    connector = BackendApiConnector.get()
    response = connector.fetch_preview_items(identifier=identifier, limit=1)
    if len(response.items) != 1:
        msg = f"No item found for identifier '{identifier}'"
        raise EmptySearchResultError(msg)
    title = transform_models_to_title(response.items)[0]
    return f"{title.text}"


async def resolve_editor_value(editor_value: EditorValue) -> None:
    """Resolve editor text values to human readable display values."""
    if editor_value.identifier:
        editor_value.text = await resolve_identifier(editor_value.identifier)
    else:
        msg = f"Cannot resolve editor value: {editor_value}"
        raise MExError(msg)


def load_settings() -> EditorSettings:
    """Reset the settings store and fetch the editor settings."""
    SETTINGS_STORE.reset()
    return EditorSettings.get()
