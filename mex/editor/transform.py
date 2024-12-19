from collections.abc import Sequence

import pytz
from babel.dates import format_datetime

from mex.common.exceptions import MExError
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleModel,
)
from mex.common.types import (
    Identifier,
    Link,
    TemporalEntity,
    TemporalEntityPrecision,
    Text,
    VocabularyEnum,
)
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE, EditorValue

_DEFAULT_LOCALE = "de_DE"
_DEFAULT_TIMEZONE = pytz.timezone("Europe/Berlin")
_BABEL_FORMATS_BY_PRECISION = {
    TemporalEntityPrecision.YEAR: "yyyy",
    TemporalEntityPrecision.MONTH: "MMMM yyyy",
    TemporalEntityPrecision.DAY: "d. MMMM yyyy",
    TemporalEntityPrecision.HOUR: "d. MMMM yyyy k a",
    TemporalEntityPrecision.MINUTE: "d. MMMM yyyy H:MM",
    TemporalEntityPrecision.SECOND: "d. MMMM yyyy H:MM:ss",
    TemporalEntityPrecision.MICROSECOND: "d. MMMM yyyy H:MM:ss:SS",
}


def ensure_list(values: object) -> list[object]:
    """Wrap single objects in lists, replace None with [] and return lists untouched."""
    if values is None:
        return []
    if isinstance(values, list):
        return values
    return [values]


def transform_values(values: object, allow_link: bool = True) -> list[EditorValue]:
    """Convert a single object or a list of objects into a list of editor values."""
    return [transform_value(v, allow_link) for v in ensure_list(values)]


def transform_value(value: object, allow_link: bool = True) -> EditorValue:
    """Transform a single object into an editor value ready for rendering."""
    if isinstance(value, Text):
        return EditorValue(
            text=value.value,
            badge=value.language,
        )
    if isinstance(value, Link):
        return EditorValue(
            text=value.title or value.url,
            href=value.url if allow_link else None,
            badge=value.language,
            external=True,
        )
    if isinstance(value, Identifier):
        return EditorValue(
            text=str(value),
            href=f"/item/{value}" if allow_link else None,
        )
    if isinstance(value, VocabularyEnum):
        return EditorValue(
            text=value.name,
            badge=type(value).__name__,
        )
    if isinstance(value, TemporalEntity):
        return EditorValue(
            text=format_datetime(
                _DEFAULT_TIMEZONE.localize(value.date_time),
                format=_BABEL_FORMATS_BY_PRECISION[value.precision],
                locale=_DEFAULT_LOCALE,
            ),
            badge=value.precision.value,
        )
    if isinstance(value, str):
        return EditorValue(
            text=str(value),
        )
    msg = f"cannot transform {type(value).__name__} to editor value"
    raise MExError(msg)


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
