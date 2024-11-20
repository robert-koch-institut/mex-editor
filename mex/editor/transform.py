from collections.abc import Sequence

import pytz
from babel.dates import format_datetime

from mex.common.exceptions import MExError
from mex.common.models import AnyExtractedModel, AnyMergedModel
from mex.common.types import (
    Identifier,
    Link,
    TemporalEntity,
    TemporalEntityPrecision,
    Text,
    VocabularyEnum,
)
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE, FixedValue

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


def transform_values(values: object) -> list[FixedValue]:
    """Convert a single object or a list of objects into a list of fixed values."""
    if values is None:
        return []
    if not isinstance(values, list):
        values = [values]
    return [transform_value(v) for v in values]


def transform_value(value: object) -> FixedValue:
    """Transform a single object into a fixed value ready for rendering."""
    if isinstance(value, Text):
        return FixedValue(
            text=value.value,
            badge=value.language,
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
        )
    if isinstance(value, VocabularyEnum):
        return FixedValue(
            text=value.name,
            badge=type(value).__name__,
        )
    if isinstance(value, TemporalEntity):
        return FixedValue(
            text=format_datetime(
                _DEFAULT_TIMEZONE.localize(value.date_time),
                format=_BABEL_FORMATS_BY_PRECISION[value.precision],
                locale=_DEFAULT_LOCALE,
            ),
        )
    if value is not None:
        return FixedValue(
            text=str(value),
        )
    msg = "cannot transform null value to renderable object"
    raise MExError(msg)


def transform_models_to_stem_type(
    models: Sequence[AnyExtractedModel | AnyMergedModel],
) -> str | None:
    """Get the stem type from a list of models."""
    if not models:
        return None
    return models[0].stemType


def transform_models_to_title(
    models: Sequence[AnyExtractedModel | AnyMergedModel],
) -> list[FixedValue]:
    """Convert a list of models into fixed values based on the title config."""
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
