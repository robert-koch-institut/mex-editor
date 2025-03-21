from async_lru import alru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyPreviewModel, PaginatedItemsContainer
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
    result, *_ = transform_models_to_results(container.items)
    return f"{result.title[0].display_text}"
