import pytest

from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AdditiveActivity,
    AdditiveContactPoint,
    AnyAdditiveModel,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreventiveModel,
    AnyRuleModel,
    AnySubtractiveModel,
    ExtractedContactPoint,
    ExtractedPerson,
    MergedConsent,
    MergedContactPoint,
    PreventivePerson,
    SubtractiveActivity,
    SubtractivePerson,
)
from mex.common.types import (
    ConsentStatus,
    Link,
    LinkLanguage,
    MergedActivityIdentifier,
    MergedContactPointIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    YearMonthDayTime,
)
from mex.editor.edit.models import EditorField, EditorPrimarySource
from mex.editor.edit.transform import (
    _get_primary_source_id_from_model,
    _transform_model_to_editor_primary_source,
    _transform_model_values_to_editor_values,
)
from mex.editor.models import EditorValue


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (
            ExtractedContactPoint(
                email="info@rki.de",
                hadPrimarySource=MergedPrimarySourceIdentifier(
                    "gGdOIbDIHRt35He616Fv5q"
                ),
                identifierInPrimarySource="info",
            ),
            MergedPrimarySourceIdentifier("gGdOIbDIHRt35He616Fv5q"),
        ),
        (
            MergedContactPoint(
                identifier=MergedContactPointIdentifier("t35He616Fv5qxGdOIbDiHR"),
                email="info@rki.de",
            ),
            MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        ),
        (
            AdditiveContactPoint(
                email="example@rki.de",
            ),
            MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        ),
    ],
)
def test_get_primary_source_id_from_model(
    model: AnyExtractedModel | AnyMergedModel | AnyRuleModel,
    expected: MergedPrimarySourceIdentifier,
) -> None:
    primary_source_id = _get_primary_source_id_from_model(model)
    assert primary_source_id == expected


@pytest.mark.parametrize(
    ("model", "field_name", "subtractive", "expected"),
    [
        (
            MergedConsent(
                identifier=MergedContactPointIdentifier.generate(),
                hasConsentStatus=ConsentStatus["VALID_FOR_PROCESSING"],
                hasDataSubject=MergedPersonIdentifier.generate(),
                isIndicatedAtTime=YearMonthDayTime("2022-09-30T20:48:35Z"),
            ),
            "hasConsentStatus",
            None,
            [EditorValue(text="VALID_FOR_PROCESSING", badge="ConsentStatus")],
        ),
        (
            ExtractedPerson(
                identifierInPrimarySource="example",
                hadPrimarySource=MergedPrimarySourceIdentifier.generate(),
                fullName=["Example, Name", "Dr. Example"],
            ),
            "fullName",
            None,
            [
                EditorValue(text="Example, Name"),
                EditorValue(text="Dr. Example"),
            ],
        ),
        (
            AdditiveActivity(
                succeeds=[
                    MergedActivityIdentifier("gGdOIbDIHRt35He616Fv5q"),
                ]
            ),
            "succeeds",
            SubtractiveActivity(
                isPartOfActivity=[MergedActivityIdentifier("doesNotMatter000000000")]
            ),
            [
                EditorValue(
                    text="gGdOIbDIHRt35He616Fv5q", href="/item/gGdOIbDIHRt35He616Fv5q"
                ),
            ],
        ),
        (
            AdditiveActivity(
                documentation=[
                    Link(
                        url="http://example",
                        title="Example Homepage",
                        language=LinkLanguage.EN,
                    ),
                    Link(url="http://pavyzdys"),
                ]
            ),
            "documentation",
            SubtractiveActivity(
                documentation=[
                    Link(
                        url="http://example",
                        title="Example Homepage",
                        language=LinkLanguage.EN,
                    ),
                ]
            ),
            [
                EditorValue(
                    text="Example Homepage",
                    badge="en",
                    href="http://example",
                    external=True,
                    enabled=False,
                ),
                EditorValue(
                    text="http://pavyzdys",
                    href="http://pavyzdys",
                    external=True,
                    enabled=True,
                ),
            ],
        ),
    ],
    ids=["single value", "list", "irrelevant subtractive", "subtractive applied"],
)
def test_transform_model_values_to_editor_values(
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    field_name: str,
    subtractive: AnySubtractiveModel | None,
    expected: EditorValue,
) -> None:
    editor_value = _transform_model_values_to_editor_values(
        model, field_name, subtractive
    )
    assert editor_value == expected


@pytest.mark.parametrize(
    (
        "model",
        "subtractive",
        "preventive",
        "expected_given_name",
        "expected_family_name",
    ),
    [
        (
            ExtractedPerson(
                identifierInPrimarySource="example",
                hadPrimarySource=MergedPrimarySourceIdentifier("primarySourceId"),
                givenName=["Example"],
            ),
            None,
            None,
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId", href="/item/primarySourceId"
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    editor_values=[EditorValue(text="Example")],
                )
            ],
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId", href="/item/primarySourceId"
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    editor_values=[],
                )
            ],
        ),
        (
            ExtractedPerson(
                identifierInPrimarySource="given-family",
                hadPrimarySource=MergedPrimarySourceIdentifier("primarySourceId"),
                givenName=["Given", "Gegeben"],
                familyName=["Family"],
            ),
            SubtractivePerson(
                givenName=["Gegeben"],
            ),
            PreventivePerson(
                familyName=[MergedPrimarySourceIdentifier("primarySourceId")]
            ),
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId", href="/item/primarySourceId"
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    editor_values=[
                        EditorValue(text="Given"),
                        EditorValue(text="Gegeben", enabled=False),
                    ],
                )
            ],
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId", href="/item/primarySourceId"
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    editor_values=[EditorValue(text="Family")],
                    enabled=False,
                )
            ],
        ),
    ],
    ids=["without rules", "with rules"],
)
def test_transform_model_to_editor_primary_source(
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    subtractive: AnySubtractiveModel | None,
    preventive: AnyPreventiveModel | None,
    expected_given_name: list[EditorPrimarySource],
    expected_family_name: list[EditorPrimarySource],
) -> None:
    given_name = EditorField(name="givenName", primary_sources=[])
    family_name = EditorField(name="familyName", primary_sources=[])
    fields_by_name = {"givenName": given_name, "familyName": family_name}

    _transform_model_to_editor_primary_source(
        fields_by_name, model, subtractive, preventive
    )

    assert given_name.primary_sources == expected_given_name
    assert family_name.primary_sources == expected_family_name


def test_transform_models_to_fields() -> None:
    pass


def test_transform_field_to_preventive() -> None:
    pass


def test_transform_render_value_to_model_type() -> None:
    pass


def test_transform_field_to_subtractive() -> None:
    pass


def test_transform_fields_to_rule_set() -> None:
    pass
