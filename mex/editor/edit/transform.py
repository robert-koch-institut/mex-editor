import functools
from collections.abc import Iterable

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    AnyRuleModel,
)
from mex.common.types import Identifier, Link, Text
from mex.editor.edit.models import EditableField, EditablePrimarySource, FixedValue
from mex.editor.transform import render_model_title


@functools.lru_cache(maxsize=500)
def get_title(merged_identifier: str) -> str:
    """Get a cached preview title for a given merged identifier."""
    connector = BackendApiConnector.get()
    item = connector.get_merged_item(merged_identifier)
    return render_model_title(item)


def _transform_values(values: object) -> list[FixedValue]:
    if not isinstance(values, list):
        values = [values]
    return [_transform_value(v) for v in values]


def _transform_value(value: object) -> FixedValue:
    if value is None:
        return FixedValue(
            text=None,
            href=None,
            language=None,
            external=False,
        )
    if isinstance(value, Text):
        return FixedValue(
            text=value.value,
            language=value.language,
            href=None,
            external=False,
        )
    if isinstance(value, Link):
        return FixedValue(
            text=value.title or value.url,
            href=value.url,
            language=value.language,
            external=True,
        )
    if isinstance(value, Identifier):
        return FixedValue(
            text=get_title(value),
            href=f"/item/{value}",
            language=None,
            external=False,
        )
    return FixedValue(
        text=str(value),
        href=None,
        language=None,
        external=False,
    )


def transform_models_to_fields(
    models: Iterable[AnyExtractedModel | AnyRuleModel],
) -> list[EditableField]:
    """Convert a list of extracted models into editable field models."""
    fields_by_name: dict[str, EditableField] = {}
    for model in models:
        if isinstance(model, AnyExtractedModel):
            primary_source_name = _transform_value(model.hadPrimarySource)
        else:
            primary_source_name = _transform_value(MEX_PRIMARY_SOURCE_STABLE_TARGET_ID)

        for field_name in model.model_fields:
            editable_field = EditableField(name=field_name, primary_sources=[])
            fields_by_name.setdefault(field_name, editable_field)
            values = _transform_values(getattr(model, field_name))
            editable_field.primary_sources.append(
                EditablePrimarySource(name=primary_source_name, values=values)
            )
    return list(fields_by_name.values())
