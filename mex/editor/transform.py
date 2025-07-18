from collections.abc import Sequence

from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleModel,
)
from mex.common.types import Identifier, Link, TemporalEntity, Text, VocabularyEnum
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE, EditorValue


def ensure_list(values: object) -> list[object]:
    """Wrap single objects in lists, replace None with [] and return lists untouched."""
    if values is None:
        return []
    if isinstance(values, list):
        return values
    return [values]


def transform_values(
    values: object,
    allow_link: bool = True,  # noqa: FBT001, FBT002
) -> list[EditorValue]:
    """Convert a single object or a list of objects into a list of editor values."""
    return [transform_value(v, allow_link) for v in ensure_list(values)]


def transform_value(
    value: object,
    allow_link: bool = True,  # noqa: FBT001, FBT002
) -> EditorValue:
    """Transform a single object into an editor value ready for rendering."""
    if isinstance(value, Text):
        return EditorValue(
            text=value.value,
            badge=value.language.name if value.language else None,
        )
    if isinstance(value, Link):
        return EditorValue(
            text=value.title,
            href=value.url if allow_link else None,
            badge=value.language.name if value.language else None,
            external=True,
        )
    if isinstance(value, Identifier):
        return EditorValue(
            identifier=str(value),
            href=f"/item/{value}" if allow_link else None,
        )
    if isinstance(value, VocabularyEnum):
        return EditorValue(
            text=type(value).__name__,
            badge=value.name,
        )
    if isinstance(value, TemporalEntity):
        return EditorValue(
            text=str(value),
            badge=value.precision.value,
        )
    if isinstance(value, str | int):
        return EditorValue(
            text=str(value),
        )
    msg = f"cannot transform {type(value).__name__} to editor value"
    raise NotImplementedError(msg)


def transform_models_to_stem_type(
    models: Sequence[
        AnyRuleModel | AnyExtractedModel | AnyPreviewModel | AnyMergedModel
    ],
) -> str | None:
    """Get the stem type from a list of models."""
    if not models:
        return None
    return models[0].stemType


def transform_models_to_title(
    models: Sequence[
        AnyRuleModel | AnyExtractedModel | AnyPreviewModel | AnyMergedModel
    ],
) -> list[EditorValue]:
    """Convert a list of models into editor values based on the title config."""
    if not models:
        return []
    titles: list[EditorValue] = []
    for model in models:
        config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
        titles.extend(
            transform_values(getattr(model, config.title), allow_link=False),
        )
    if titles:
        return titles
    return transform_values(transform_models_to_stem_type(models))


def transform_models_to_preview(
    models: Sequence[
        AnyRuleModel | AnyExtractedModel | AnyPreviewModel | AnyMergedModel
    ],
) -> list[EditorValue]:
    """Converts a list of models into editor values based on the preview config."""
    if not models:
        return []
    previews: list[EditorValue] = []
    for model in models:
        config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
        previews.extend(
            value
            for field in config.preview
            for value in transform_values(getattr(model, field), allow_link=False)
        )
    if previews:
        return previews
    return transform_values(transform_models_to_stem_type(models))
