from collections.abc import Sequence

from mex.common.models import AnyExtractedModel, AnyMergedModel
from mex.common.types import Identifier, Link, Text, VocabularyEnum
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE, FixedValue


def transform_values(values: object) -> list[FixedValue]:
    """Convert a single object or a list of objects into a list of fixed values."""
    if values is None:
        return []
    if not isinstance(values, list):
        values = [values]
    return [transform_value(v) for v in values]


def transform_value(value: object) -> FixedValue:
    """Transform a single object into a fixed value ready for rendering."""
    if value is None:
        return FixedValue(
            text=None,
            href=None,
            badge=None,
            external=False,
        )
    if isinstance(value, Text):
        return FixedValue(
            text=value.value,
            badge=value.language,
            href=None,
            external=False,
        )
    if isinstance(value, Link):
        return FixedValue(
            text=value.title or value.url,
            href=value.url,
            badge=value.language,
            external=True,
        )
    if isinstance(value, Identifier):
        return FixedValue(
            text=value,
            href=f"/item/{value}",
            badge=None,
            external=False,
        )
    if isinstance(value, VocabularyEnum):
        return FixedValue(
            text=value.name,
            href=None,
            badge=type(value).__name__,
            external=False,
        )
    return FixedValue(
        text=str(value),
        href=None,
        badge=None,
        external=False,
    )


def transform_models_to_title(
    models: Sequence[AnyExtractedModel | AnyMergedModel],
) -> list[FixedValue]:
    """Converts a list of models into fixed values based on the title config."""
    if not models:
        return []
    titles: list[FixedValue] = []
    for model in models:
        config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
        titles.extend(
            transform_values(getattr(model, config.title)),
        )
    if titles:
        return titles
    return transform_values(models[0].identifier)


def transform_models_to_preview(
    models: Sequence[AnyExtractedModel | AnyMergedModel],
) -> list[FixedValue]:
    """Converts a list of models into fixed values based on the preview config."""
    if not models:
        return []
    previews: list[FixedValue] = []
    for model in models:
        config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
        previews.extend(
            value
            for field in config.preview
            for value in transform_values(getattr(model, field))
        )
    if previews:
        return previews
    return transform_values(models[0].entityType)
