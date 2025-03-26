from async_lru import alru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import EmptySearchResultError, MExError
from mex.common.models import AnyPreviewModel, PaginatedItemsContainer
from mex.editor.models import EditorValue
from mex.editor.search.transform import transform_models_to_results


@alru_cache
async def resolve_identifier(identifier: str) -> str:
    """Resolve identifiers to human readable display values."""
    # TODO(HS): use the user auth for backend requests (stop-gap MX-1616)
    connector = BackendApiConnector.get()
    # TODO(HS): use proper connector method when available (stop-gap MX-1762)
    response = connector.request(
        method="GET",
        endpoint="preview-item",
        params={
            "identifier": identifier,
            "skip": "0",
            "limit": "1",
        },
    )
    container = PaginatedItemsContainer[AnyPreviewModel].model_validate(response)
    if len(container.items) != 1:
        msg = f"No item found for identifier '{identifier}'"
        raise EmptySearchResultError(msg)
    result, *_ = transform_models_to_results(container.items)
    return f"{result.title[0].display_text}"


async def resolve_editor_value(editor_value: EditorValue) -> None:
    """Resolve editor text values to human readable display values."""
    if editor_value.is_identifier:
        editor_value.display_text = await resolve_identifier(editor_value.text)
        editor_value.resolved = True
    else:
        msg = f"Cannot resolve editor value: {editor_value}"
        raise MExError(msg)
