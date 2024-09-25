from collections.abc import Iterable

from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    AnyRuleModel,
)
from mex.common.types import Identifier, Link, Text
from mex.editor.edit.models import EditableField, EditablePrimarySource, FixedValue
from mex.editor.transform import get_title_for_merged_id


def _transform_values(values: object) -> list[FixedValue]:
    if values is None:
        return []
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
            text=get_title_for_merged_id(value),
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
            primary_source_name = _transform_value(Identifier(model.hadPrimarySource))
        elif isinstance(model, AnyRuleModel):
            primary_source_name = _transform_value(MEX_PRIMARY_SOURCE_STABLE_TARGET_ID)
        else:
            raise RuntimeError(f"{model} is weird")
        for field_name in model.model_fields:
            editable_field = EditableField(name=field_name, primary_sources=[])
            fields_by_name.setdefault(field_name, editable_field)
            if values := _transform_values(getattr(model, field_name)):
                editable_field.primary_sources.append(
                    EditablePrimarySource(name=primary_source_name, values=values)
                )
    return list(fields_by_name.values())
