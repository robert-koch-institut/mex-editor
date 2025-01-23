from collections.abc import Iterable, Sequence

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_stem_type,
    transform_models_to_title,
    transform_values,
)


def transform_models_to_results(models: Iterable[AnyExtractedModel]) -> list[AuxResult]:
    """Convert a list of extracted models into aux search result models."""
    return [
        AuxResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            all_properties=models_to_all_properties([model]),
            show_properties=True,
        )
        for model in models
    ]


def models_to_all_properties(models: Sequence[AnyExtractedModel]) -> list[EditorValue]:
    """Transform all properties of a model into a dictionary."""
    if not models:
        return []
    all_properties_lists: list[EditorValue] = []
    for model in models:
        attributes = {attr: getattr(model, attr) for attr in vars(model)}
        all_properties_lists.extend(
            value
            for field_value in attributes
            for value in transform_values(getattr(model, field_value), allow_link=False)
        )
    if all_properties_lists:
        return all_properties_lists
    return transform_values(transform_models_to_stem_type(models))
