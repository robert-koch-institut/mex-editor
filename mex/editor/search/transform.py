from collections.abc import Iterable

from mex.common.models import AnyMergedModel
from mex.editor.search.models import SearchResult
from mex.editor.transform import transform_models_to_preview, transform_models_to_title


def transform_models_to_results(models: Iterable[AnyMergedModel]) -> list[SearchResult]:
    """Convert a list of merged models into search result models."""
    return [
        SearchResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
        )
        for model in models
    ]
