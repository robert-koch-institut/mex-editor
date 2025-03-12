from collections.abc import Iterable

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_title,
    transform_values,
)


def transform_models_to_results(models: Iterable[AnyExtractedModel]) -> list[AuxResult]:
    """Convert a list of extracted models into a list of aux search result models."""
    return [
        AuxResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            all_properties=model_to_all_properties(model),
            show_properties=False,
            show_import_button=True,
        )
        for model in models
    ]


def model_to_all_properties(model: AnyExtractedModel) -> list[EditorValue]:
    """Transform all properties of a model into a list of EditorValues."""
    return [
        value
        for field_name in model.model_fields
        for value in transform_values(getattr(model, field_name), allow_link=False)
    ]
