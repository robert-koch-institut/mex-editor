from mex.common.fields import (
    LINK_FIELDS_BY_CLASS_NAME,
    TEMPORAL_FIELDS_BY_CLASS_NAME,
    TEXT_FIELDS_BY_CLASS_NAME,
    VOCABULARY_FIELDS_BY_CLASS_NAME,
)
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    RULE_SET_REQUEST_CLASSES_BY_NAME,
    AnyAdditiveModel,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreventiveModel,
    AnyRuleModel,
    AnyRuleSetRequest,
    AnySubtractiveModel,
)
from mex.common.transform import ensure_postfix, ensure_prefix
from mex.common.types import (
    TEMPORAL_ENTITY_CLASSES_BY_PRECISION,
    VOCABULARY_ENUMS_BY_NAME,
    AnyNestedModel,
    AnyPrimitiveType,
    AnyTemporalEntity,
    AnyVocabularyEnum,
    Link,
    MergedPrimarySourceIdentifier,
    TemporalEntityPrecision,
    Text,
)
from mex.editor.edit.models import EditableField, EditablePrimarySource
from mex.editor.models import FixedValue
from mex.editor.transform import transform_value, transform_values


def _get_primary_source_id_from_model(
    model: AnyExtractedModel | AnyMergedModel | AnyRuleModel,
) -> MergedPrimarySourceIdentifier:
    if isinstance(model, AnyExtractedModel):
        return MergedPrimarySourceIdentifier(model.hadPrimarySource)
    if isinstance(model, AnyMergedModel | AnyRuleModel):
        return MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
    msg = (
        "cannot transform model, expected extracted ExtractedData or "
        f"MergedItem or RuleItem, got {type(model).__name__}"
    )
    raise TypeError(msg)


def _transform_model_to_field(
    fields_by_name: dict[str, EditableField],
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    subtractive: AnySubtractiveModel | None,
    preventive: AnyPreventiveModel | None,
) -> None:
    primary_source_id = _get_primary_source_id_from_model(model)
    primary_source_name = transform_value(primary_source_id)
    for field_name in model.model_fields:
        editable_field = fields_by_name.setdefault(
            field_name, EditableField(name=field_name, primary_sources=[])
        )
        values = transform_values(getattr(model, field_name))
        for value in values:
            value.enabled = not (
                subtractive and value in getattr(subtractive, field_name)
            )
        editable_field.primary_sources.append(
            EditablePrimarySource(
                name=primary_source_name,
                identifier=primary_source_id,
                editor_values=values,
                enabled=preventive
                and (primary_source_id not in getattr(preventive, field_name)),
            )
        )


def transform_models_to_fields(
    *models: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    subtractive: AnySubtractiveModel | None = None,
    preventive: AnyPreventiveModel | None = None,
) -> list[EditableField]:
    """Convert a list of models into editable field models."""
    fields_by_name: dict[str, EditableField] = {}
    for model in models:
        _transform_model_to_field(fields_by_name, model, subtractive, preventive)
    return list(fields_by_name.values())


def _transform_field_to_preventive(
    field: EditableField, preventive: AnyPreventiveModel
) -> None:
    if (prevented_sources := getattr(preventive, field.name)) is not None:
        for primary_source in field.primary_sources:
            if not primary_source.enabled and (
                primary_source.identifier not in prevented_sources
            ):
                prevented_sources.append(primary_source.identifier)


def _transform_fixed_value_to_model_type(
    value: FixedValue, field_name: str, class_name: str
) -> AnyNestedModel | AnyPrimitiveType | AnyTemporalEntity | AnyVocabularyEnum:
    if field_name in LINK_FIELDS_BY_CLASS_NAME[class_name]:
        return Link(url=value.href, language=value.badge, title=value.text)
    if field_name in TEXT_FIELDS_BY_CLASS_NAME[class_name]:
        return Text(language=value.badge, value=value.text)
    if field_name in VOCABULARY_FIELDS_BY_CLASS_NAME[class_name]:
        return VOCABULARY_ENUMS_BY_NAME[str(value.badge)][str(value.text)]
    if field_name in TEMPORAL_FIELDS_BY_CLASS_NAME[class_name]:
        precision = TemporalEntityPrecision(value.badge)
        temporal_class = TEMPORAL_ENTITY_CLASSES_BY_PRECISION[precision]
        return temporal_class(str(value.text), precision=precision)
    return value.text


def _transform_field_to_subtractive(
    field: EditableField, subtractive: AnySubtractiveModel
) -> None:
    class_name = ensure_prefix("Merged", subtractive.stemType)
    if (subtracted_values := getattr(subtractive, field.name)) is not None:
        for primary_source in field.primary_sources:
            for value in primary_source.editor_values:
                if not value.enabled:
                    subtracted_value = _transform_fixed_value_to_model_type(
                        value,
                        field.name,
                        class_name,
                    )
                    if subtracted_value not in subtracted_values:
                        subtracted_values.append(subtracted_value)


def transform_fields_to_rule_set(
    stem_type: str, fields: list[EditableField]
) -> AnyRuleSetRequest:
    """Transform the given fields to a rule set of the given stem type."""
    rule_set_class = RULE_SET_REQUEST_CLASSES_BY_NAME[
        ensure_postfix(stem_type, "RuleSetRequest")
    ]
    rule_set = rule_set_class()
    for field in fields:
        _transform_field_to_preventive(field, rule_set.preventive)
        _transform_field_to_subtractive(field, rule_set.subtractive)
    return rule_set
