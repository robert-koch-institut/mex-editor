from collections.abc import Iterable

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_title,
    transform_value,
)


def transform_models_to_results(models: Iterable[AnyExtractedModel]) -> list[AuxResult]:
    """Convert a list of extracted models into aux search result models."""
    return [
        AuxResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            all_properties=transform_all_properties(model),
            show_properties=True,
        )
        for model in models
    ]


def transform_all_properties(model: AnyExtractedModel) -> list[EditorValue]:
    """Transform all properties of a model into a dictionary."""
    return [
        transform_value(getattr(model, attr))
        for attr in dict(model)
        if not attr.startswith("_")
    ]
