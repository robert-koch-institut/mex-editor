from collections.abc import Iterable

from mex.common.models import AnyMergedModel
from mex.editor.search.models import SearchResult
from mex.editor.transform import render_model_preview, render_model_title


def transform_models_to_results(models: Iterable[AnyMergedModel]) -> list[SearchResult]:
    """Convert a list of merged models into search result models."""
    return [
        SearchResult(
            identifier=model.identifier,
            title=render_model_title(model),
            preview=render_model_preview(model),
        )
        for model in models
    ]
