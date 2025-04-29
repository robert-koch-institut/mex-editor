from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import (
    AnyAdditiveModel,
    AnyPreventiveModel,
    AnySubtractiveModel,
)
from mex.editor.edit.models import EditorField
from mex.editor.edit.transform import _transform_model_to_editor_primary_sources


def transform_model_to_template_fields(
    entity_type: str,
    additive: AnyAdditiveModel,
    subtractive: AnySubtractiveModel,
    preventive: AnyPreventiveModel,
) -> list[EditorField]:
    """Convert the given models and rules into editor field models.

    Args:
        entity_type: Entity type of the model
        additive: An additive rule model
        subtractive: A subtractive rule model
        preventive: A preventive rule model

    Returns:
        A list of editor field instances
    """
    mergeable_fields = sorted(MERGEABLE_FIELDS_BY_CLASS_NAME[entity_type])
    fields_by_name = {
        field_name: EditorField(name=field_name, primary_sources=[])
        for field_name in mergeable_fields
    }
    _transform_model_to_editor_primary_sources(
        fields_by_name,
        additive,
        subtractive,
        preventive,
    )
    return list(fields_by_name.values())
