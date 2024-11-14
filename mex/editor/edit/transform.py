from collections.abc import Iterable

from mex.common.exceptions import MExError
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    AnyRuleModel,
)
from mex.common.types import Identifier
from mex.editor.edit.models import EditableField, EditablePrimarySource
from mex.editor.transform import transform_value, transform_values


def transform_models_to_fields(
    models: Iterable[AnyExtractedModel | AnyRuleModel],
) -> list[EditableField]:
    """Convert a list of extracted models into editable field models."""
    fields_by_name: dict[str, EditableField] = {}
    for model in models:
        if isinstance(model, AnyExtractedModel):
            primary_source_name = transform_value(Identifier(model.hadPrimarySource))
        elif isinstance(model, AnyRuleModel):
            primary_source_name = transform_value(MEX_PRIMARY_SOURCE_STABLE_TARGET_ID)
        else:
            msg = (
                "cannot transform model, expected extracted ExtractedData or "
                f"RuleItem, got {type(model).__name__}"
            )
            raise MExError(msg)
        for field_name in model.model_fields:
            editable_field = EditableField(name=field_name, primary_sources=[])
            fields_by_name.setdefault(field_name, editable_field)
            if values := transform_values(getattr(model, field_name)):
                editable_field.primary_sources.append(
                    EditablePrimarySource(
                        name=primary_source_name, editor_values=values
                    )
                )
    return list(fields_by_name.values())
