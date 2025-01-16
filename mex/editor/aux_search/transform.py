from collections.abc import Iterable

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.transform import transform_models_to_preview, transform_models_to_title


def transform_models_to_results(models: Iterable[AnyExtractedModel]) -> list[AuxResult]:
    """Convert a list of extracted models into aux search result models."""
    return [
        AuxResult(
            identifier=model.identifier,
            title=transform_models_to_title([model]),
            preview=transform_models_to_preview([model]),
            show_properties=False,
        )
        for model in models
    ]
