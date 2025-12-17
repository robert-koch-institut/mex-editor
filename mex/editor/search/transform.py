from collections.abc import Iterable

from mex.common.models import AnyExtractedModel, AnyPreviewModel
from mex.editor.models import EditorValue
from mex.editor.search.models import ReferenceDialogSearchResult, SearchResult
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_title,
    transform_values,
)


def transform_models_to_results(
    models: Iterable[AnyPreviewModel | AnyExtractedModel],
) -> list[SearchResult]:
    """Convert a list of models into a list of search result models."""
    return [
        SearchResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            stem_type=model.stemType,
        )
        for model in models
    ]


def transform_models_to_dialog_results(
    models: Iterable[AnyPreviewModel | AnyExtractedModel],
) -> list[ReferenceDialogSearchResult]:
    """Convert a list of models into a list of search result models."""
    return [
        ReferenceDialogSearchResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            all_properties=transform_model_to_all_properties(model),
            stem_type=model.stemType,
        )
        for model in models
    ]


def transform_model_to_all_properties(
    model: AnyExtractedModel | AnyPreviewModel,
) -> list[EditorValue]:
    """Transform all properties of a model into a list of EditorValues."""
    return [
        value
        for field_name in model.model_fields
        for value in transform_values(getattr(model, field_name), allow_link=False)
    ]
