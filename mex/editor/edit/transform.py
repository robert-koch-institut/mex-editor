from collections.abc import Iterable

from mex.common.exceptions import MExError
from mex.common.models import (
    ADDITIVE_MODEL_CLASSES_BY_NAME,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    PREVENTIVE_MODEL_CLASSES_BY_NAME,
    RULE_SET_REQUEST_CLASSES_BY_NAME,
    SUBTRACTIVE_MODEL_CLASSES_BY_NAME,
    AnyExtractedModel,
    AnyMergedModel,
    AnyRuleModel,
    AnyRuleSetRequest,
)
from mex.common.transform import ensure_postfix, ensure_prefix
from mex.common.types import (
    Identifier,
    Link,
    TemporalEntity,
    TemporalEntityPrecision,
    Text,
)
from mex.editor.edit.fields import (
    LINK_FIELDS_BY_CLASS_NAME,
    NEVER_EDITABLE_FIELDS,
    TEMPORAL_FIELDS_BY_CLASS_NAME,
    TEXT_FIELDS_BY_CLASS_NAME,
    VOCABULARY_CLASSES_BY_NAME,
    VOCABULARY_FIELDS_BY_CLASS_NAME,
)
from mex.editor.edit.models import EditableField, EditablePrimarySource
from mex.editor.transform import transform_value, transform_values


def transform_models_to_fields(
    models: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleModel],
) -> list[EditableField]:
    """Convert a list of models into editable field models."""
    fields_by_name: dict[str, EditableField] = {}
    for model in models:
        if isinstance(model, AnyExtractedModel):
            primary_source_id = Identifier(model.hadPrimarySource)
        elif isinstance(model, AnyMergedModel | AnyRuleModel):
            primary_source_id = MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
        else:
            msg = (
                "cannot transform model, expected extracted ExtractedData or "
                f"MergedItem or RuleItem, got {type(model).__name__}"
            )
            raise MExError(msg)
        primary_source_name = transform_value(primary_source_id)
        for field_name in model.model_fields:
            editable_field = EditableField(name=field_name, primary_sources=[])
            fields_by_name.setdefault(field_name, editable_field)
            if values := transform_values(getattr(model, field_name)):
                editable_field.primary_sources.append(
                    EditablePrimarySource(
                        name=primary_source_name,
                        identifier=primary_source_id,
                        editor_values=values,
                    )
                )
    return list(fields_by_name.values())


def rule_set_for_stem_type(stem_type: str) -> AnyRuleSetRequest:
    rule_set_class = RULE_SET_REQUEST_CLASSES_BY_NAME[
        ensure_postfix(stem_type, "RuleSetRequest")
    ]
    additive_class = ADDITIVE_MODEL_CLASSES_BY_NAME[
        ensure_prefix(stem_type, "Additive")
    ]
    subtractive_class = SUBTRACTIVE_MODEL_CLASSES_BY_NAME[
        ensure_prefix(stem_type, "Subtractive")
    ]
    preventive_class = PREVENTIVE_MODEL_CLASSES_BY_NAME[
        ensure_prefix(stem_type, "Preventive")
    ]
    return rule_set_class(
        additive=additive_class(),
        subtractive=subtractive_class(),
        preventive=preventive_class(),
    )


def transform_fields_to_rule_set(
    stem_type: str, fields: list[EditableField]
) -> AnyRuleSetRequest:
    """Transform the given fields to a rule set of the given stem type."""
    rule_set = rule_set_for_stem_type(stem_type)

    for field in fields:
        if field.name in NEVER_EDITABLE_FIELDS:
            continue
        for primary_source in field.primary_sources:
            if not primary_source.enabled:
                prevented_sources = getattr(rule_set.preventive, field.name)
                if primary_source.identifier not in prevented_sources:
                    prevented_sources.append(primary_source.identifier)
            for value in primary_source.editor_values:
                subtracted_values = getattr(rule_set.subtractive, field.name)
                if not value.enabled:
                    subtracted_value: object
                    if field.name in LINK_FIELDS_BY_CLASS_NAME[f"Merged{stem_type}"]:
                        subtracted_value = Link(
                            url=value.href, language=value.badge, title=value.text
                        )
                    elif field.name in TEXT_FIELDS_BY_CLASS_NAME[f"Merged{stem_type}"]:
                        subtracted_value = Text(language=value.badge, value=value.text)
                    elif (
                        field.name
                        in VOCABULARY_FIELDS_BY_CLASS_NAME[f"Merged{stem_type}"]
                    ):
                        subtracted_value = VOCABULARY_CLASSES_BY_NAME[value.badge][
                            value.text
                        ]
                    elif (
                        field.name
                        in TEMPORAL_FIELDS_BY_CLASS_NAME[f"Merged{stem_type}"]
                    ):
                        subtracted_value = TemporalEntity(
                            value.text, precision=TemporalEntityPrecision(value.badge)
                        )
                    else:
                        subtracted_value = value.text
                    if subtracted_value not in subtracted_values:
                        subtracted_values.append(subtracted_value)

    return rule_set
