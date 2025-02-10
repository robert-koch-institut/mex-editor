from mex.common.fields import (
    EMAIL_FIELDS_BY_CLASS_NAME,
    LINK_FIELDS_BY_CLASS_NAME,
    MERGEABLE_FIELDS_BY_CLASS_NAME,
    STRING_FIELDS_BY_CLASS_NAME,
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
from mex.editor.edit.models import EditorField, EditorPrimarySource, InputConfig
from mex.editor.models import EditorValue
from mex.editor.transform import ensure_list, transform_value


def _get_primary_source_id_from_model(
    model: AnyExtractedModel | AnyMergedModel | AnyRuleModel,
) -> MergedPrimarySourceIdentifier:
    """Given any model type, try to derive a sensible primary source identifier."""
    if isinstance(model, AnyExtractedModel):
        return MergedPrimarySourceIdentifier(model.hadPrimarySource)
    if isinstance(model, AnyMergedModel | AnyRuleModel):
        return MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
    msg = (
        "Cannot get primary source ID for model. Expected ExtractedModel, "
        f"MergedModel or RuleModel, got {type(model).__name__}."
    )
    raise TypeError(msg)


def _transform_model_values_to_editor_values(
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    field_name: str,
    subtractive: AnySubtractiveModel,
) -> list[EditorValue]:
    """Given a model, a field and a subtractive rule, create editor values."""
    model_values = ensure_list(getattr(model, field_name))
    editor_values = []
    for model_value in model_values:
        editor_value = transform_value(model_value)
        # we disable the value, when either:
        editor_value.enabled = (
            # - the field is not supposed to be edited anyway, like type or id fields
            field_name not in MERGEABLE_FIELDS_BY_CLASS_NAME[subtractive.entityType]
            # - the value of the field in our model is subtracted by the given rule
            or model_value not in getattr(subtractive, field_name)
        )
        editor_values.append(editor_value)
    return editor_values


def _transform_model_to_additive_input_config(
    field_name: str,
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
) -> InputConfig | None:
    """Determine the input type for a given field of a given model."""
    if not isinstance(model, AnyAdditiveModel):
        return None
    if (
        field_name in STRING_FIELDS_BY_CLASS_NAME[model.entityType]
        or field_name in EMAIL_FIELDS_BY_CLASS_NAME[model.entityType]
    ):
        data_type = "string"
    else:
        data_type = None
    return InputConfig(data_type=data_type)


def _create_editor_primary_source(  # noqa: PLR0913
    primary_source_name: EditorValue,
    primary_source_id: MergedPrimarySourceIdentifier,
    editor_values: list[EditorValue],
    additive_values: list[EditorValue],
    field_name: str,
    preventive: AnyPreventiveModel,
    input_config: InputConfig | None,
) -> EditorPrimarySource:
    """Create a new editor primary source from the given parameters."""
    return EditorPrimarySource(
        name=primary_source_name,
        identifier=primary_source_id,
        editor_values=editor_values,
        additive_values=additive_values,
        # we disable the primary source, when either:
        enabled=(
            # - the field is not supposed to be edited anyway
            field_name not in MERGEABLE_FIELDS_BY_CLASS_NAME[preventive.entityType]
            # - the primary source was prevented by the given rule
            or primary_source_id not in getattr(preventive, field_name)
        ),
        input_config=input_config,
    )


def _transform_extracted_to_editor_primary_sources(
    fields_by_name: dict[str, EditorField],
    extracted: AnyExtractedModel,
    subtractive: AnySubtractiveModel,
    preventive: AnyPreventiveModel,
) -> None:
    """With a model and rules, attach an editor primary source to the field."""
    primary_source_id = _get_primary_source_id_from_model(extracted)
    primary_source_name = transform_value(primary_source_id)
    for field_name in extracted.model_fields:
        if field_name in fields_by_name:
            editor_values = _transform_model_values_to_editor_values(
                extracted,
                field_name,
                subtractive,
            )
            primary_source = _create_editor_primary_source(
                primary_source_name,
                primary_source_id,
                editor_values,
                [],
                field_name,
                preventive,
                None,
            )
            fields_by_name[field_name].primary_sources.append(primary_source)


def _transform_additive_to_editor_primary_sources(
    fields_by_name: dict[str, EditorField],
    additive: AnyAdditiveModel,
    subtractive: AnySubtractiveModel,
    preventive: AnyPreventiveModel,
) -> None:
    primary_source_id = _get_primary_source_id_from_model(additive)
    primary_source_name = transform_value(primary_source_id)
    for field_name in additive.model_fields:
        if field_name in fields_by_name:
            additive_values = _transform_model_values_to_editor_values(
                additive,
                field_name,
                subtractive,
            )
            input_config = _transform_model_to_additive_input_config(
                field_name,
                additive,
            )
            primary_source = _create_editor_primary_source(
                primary_source_name,
                primary_source_id,
                [],
                additive_values,
                field_name,
                preventive,
                input_config=input_config,
            )
            fields_by_name[field_name].primary_sources.append(primary_source)


def transform_models_to_fields(
    *extracted_items: AnyExtractedModel,
    additive: AnyAdditiveModel,
    subtractive: AnySubtractiveModel,
    preventive: AnyPreventiveModel,
) -> list[EditorField]:
    """Convert the given models and rules into editor field models.

    Args:
        extracted_items: A series of extracted, merged or additive models
        additive: An additive rule model
        subtractive: A subtractive rule model
        preventive: A preventive rule model

    Returns:
        A list of editor field instances
    """
    fields_by_name = {
        field_name: EditorField(name=field_name, primary_sources=[])
        for field_name in {
            f
            for e in extracted_items
            for f in MERGEABLE_FIELDS_BY_CLASS_NAME[e.entityType]
        }
    }
    for extracted in extracted_items:
        _transform_extracted_to_editor_primary_sources(
            fields_by_name, extracted, subtractive, preventive
        )
    _transform_additive_to_editor_primary_sources(
        fields_by_name, additive, subtractive, preventive
    )
    return list(fields_by_name.values())


def _transform_field_to_additive(
    field: EditorField,
    additive: AnyAdditiveModel,
) -> None:
    """Transform an editor field back to an additive rule field."""
    if field.name in MERGEABLE_FIELDS_BY_CLASS_NAME[additive.entityType]:
        additive_values = []
        for primary_source in field.primary_sources:
            for value in primary_source.additive_values:
                if value.text:
                    additive_values.append(  # noqa: PERF401
                        value.text
                    )  # TODO(ND): transform other types too
        setattr(additive, field.name, additive_values)


def _transform_field_to_preventive(
    field: EditorField,
    preventive: AnyPreventiveModel,
) -> None:
    """Transform an editor field back to a preventive rule field."""
    if field.name in MERGEABLE_FIELDS_BY_CLASS_NAME[preventive.entityType]:
        prevented_sources = getattr(preventive, field.name)
        for primary_source in field.primary_sources:
            if not primary_source.enabled and (
                primary_source.identifier not in prevented_sources
            ):
                prevented_sources.append(primary_source.identifier)


def _transform_editor_value_to_model_value(
    value: EditorValue,
    field_name: str,
    class_name: str,
) -> AnyNestedModel | AnyPrimitiveType | AnyTemporalEntity | AnyVocabularyEnum:
    """Transform an editor value back to a value to be used in mex.common.models."""
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
    field: EditorField,
    subtractive: AnySubtractiveModel,
) -> None:
    """Transform an editor field back to subtractive rule values."""
    if field.name in MERGEABLE_FIELDS_BY_CLASS_NAME[subtractive.entityType]:
        subtracted_values = getattr(subtractive, field.name)
        merged_class_name = ensure_prefix(subtractive.stemType, "Merged")
        for primary_source in field.primary_sources:
            for editor_value in [
                *primary_source.editor_values,
                *primary_source.additive_values,
            ]:
                if not editor_value.enabled:
                    subtracted_value = _transform_editor_value_to_model_value(
                        editor_value, field.name, merged_class_name
                    )
                    if subtracted_value not in subtracted_values:
                        subtracted_values.append(subtracted_value)


def transform_fields_to_rule_set(
    stem_type: str,
    fields: list[EditorField],
) -> AnyRuleSetRequest:
    """Transform the given fields to a rule set of the given stem type.

    Args:
        stem_type: The stemType the resulting rule set should have
        fields: A list of editor fields to convert into rules

    Returns:
        Any rule set request model
    """
    rule_set_class = RULE_SET_REQUEST_CLASSES_BY_NAME[
        ensure_postfix(stem_type, "RuleSetRequest")
    ]
    rule_set = rule_set_class()
    for field in fields:
        _transform_field_to_additive(field, rule_set.additive)
        _transform_field_to_preventive(field, rule_set.preventive)
        _transform_field_to_subtractive(field, rule_set.subtractive)
    return rule_set
