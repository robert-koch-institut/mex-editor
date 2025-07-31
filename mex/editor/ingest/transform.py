from collections.abc import Iterable

from mex.common.models import AnyExtractedModel
from mex.editor.ingest.models import IngestResult
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_title,
    transform_values,
)


def transform_models_to_results(
    models: Iterable[AnyExtractedModel],
) -> list[IngestResult]:
    """Convert a list of extracted models into a list of ingest result models."""
    return [
        IngestResult(
            identifier=model.identifier,
            stem_type=model.stemType,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            all_properties=model_to_all_properties(model),
            show_properties=False,
            show_ingest_button=True,
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
