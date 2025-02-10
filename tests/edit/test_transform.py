import pytest

from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AdditiveActivity,
    AdditiveContactPoint,
    AdditivePerson,
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
    MergedPerson,
    PreventivePerson,
    SubtractiveActivity,
    SubtractiveConsent,
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
    Text,
    TextLanguage,
    Year,
    YearMonthDayTime,
)
from mex.editor.edit.models import EditorField, EditorPrimarySource
from mex.editor.edit.transform import (
    _get_primary_source_id_from_model,
    _transform_editor_value_to_model_value,
    _transform_field_to_preventive,
    _transform_field_to_subtractive,
    _transform_model_to_editor_primary_sources,
    _transform_model_values_to_editor_values,
    transform_fields_to_rule_set,
    transform_models_to_fields,
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
            SubtractiveConsent(),
            [EditorValue(text="VALID_FOR_PROCESSING", badge="ConsentStatus")],
        ),
        (
            ExtractedPerson(
                identifierInPrimarySource="example",
                hadPrimarySource=MergedPrimarySourceIdentifier.generate(),
                fullName=["Example, Name", "Dr. Example"],
            ),
            "fullName",
            SubtractivePerson(),
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
                ),
            ],
        ),
    ],
    ids=["single value", "list", "irrelevant subtractive", "subtractive applied"],
)
def test_transform_model_values_to_editor_values(
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    field_name: str,
    subtractive: AnySubtractiveModel,
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
            SubtractivePerson(),
            PreventivePerson(),
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
def test_transform_model_to_editor_primary_sources(
    model: AnyExtractedModel | AnyMergedModel | AnyAdditiveModel,
    subtractive: AnySubtractiveModel,
    preventive: AnyPreventiveModel,
    expected_given_name: list[EditorPrimarySource],
    expected_family_name: list[EditorPrimarySource],
) -> None:
    given_name = EditorField(name="givenName", primary_sources=[])
    family_name = EditorField(name="familyName", primary_sources=[])
    fields_by_name = {"givenName": given_name, "familyName": family_name}

    _transform_model_to_editor_primary_sources(
        fields_by_name, model, subtractive, preventive
    )

    assert given_name.primary_sources == expected_given_name
    assert family_name.primary_sources == expected_family_name


def test_transform_models_to_fields() -> None:
    editor_fields = transform_models_to_fields(
        [
            MergedPerson(
                identifier=MergedPersonIdentifier.generate(), email=["person@rki.de"]
            )
        ],
        additive=AdditivePerson(givenName=["Good"]),
        subtractive=SubtractivePerson(givenName=["Bad"]),
        preventive=PreventivePerson(memberOf=[MEX_PRIMARY_SOURCE_STABLE_TARGET_ID]),
    )

    assert len(editor_fields) == len(MERGEABLE_FIELDS_BY_CLASS_NAME["MergedPerson"])
    fields_by_name = {f.name: f for f in editor_fields}
    assert fields_by_name["givenName"] == EditorField(
        name="givenName",
        primary_sources=[
            EditorPrimarySource(
                name=EditorValue(
                    text="00000000000000",
                    href="/item/00000000000000",
                ),
                identifier=MergedPrimarySourceIdentifier("00000000000000"),
            ),
            EditorPrimarySource(
                name=EditorValue(
                    text="00000000000000",
                    href="/item/00000000000000",
                ),
                identifier=MergedPrimarySourceIdentifier("00000000000000"),
                editor_values=[EditorValue(text="Good")],
            ),
        ],
    )
    assert fields_by_name["memberOf"] == EditorField(
        name="memberOf",
        primary_sources=[
            EditorPrimarySource(
                name=EditorValue(
                    text="00000000000000",
                    href="/item/00000000000000",
                ),
                identifier=MergedPrimarySourceIdentifier("00000000000000"),
                enabled=False,
            ),
            EditorPrimarySource(
                name=EditorValue(
                    text="00000000000000",
                    href="/item/00000000000000",
                ),
                identifier=MergedPrimarySourceIdentifier("00000000000000"),
                enabled=False,
            ),
        ],
    )


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (
            EditorField(
                name="unknownField",
                primary_sources=[
                    EditorPrimarySource(
                        enabled=True,
                        name=EditorValue(text="Enabled Primary Source"),
                        identifier=MergedPrimarySourceIdentifier(
                            "enabledPrimarySourceId"
                        ),
                    )
                ],
            ),
            {},
        ),
        (
            EditorField(
                name="familyName",
                primary_sources=[
                    EditorPrimarySource(
                        enabled=True,
                        name=EditorValue(text="Enabled Primary Source"),
                        identifier=MergedPrimarySourceIdentifier(
                            "enabledPrimarySourceId"
                        ),
                    ),
                    EditorPrimarySource(
                        enabled=False,
                        name=EditorValue(text="Prevented Primary Source"),
                        identifier=MergedPrimarySourceIdentifier(
                            "preventedPrimarySourceId"
                        ),
                    ),
                ],
            ),
            {"familyName": ["preventedPrimarySourceId"]},
        ),
    ],
)
def test_transform_field_to_preventive(
    field: EditorField, expected: dict[str, object]
) -> None:
    preventive = PreventivePerson()
    _transform_field_to_preventive(field, preventive)
    assert preventive.model_dump(exclude_defaults=True) == expected


@pytest.mark.parametrize(
    ("editor_value", "field_name", "class_name", "expected"),
    [
        (
            EditorValue(text="Titel", badge="de", href="https://beispiel"),
            "documentation",
            "MergedResource",
            Link(url="https://beispiel", language=LinkLanguage.DE, title="Titel"),
        ),
        (
            EditorValue(text="Beispiel Text", badge="de"),
            "alternativeName",
            "ExtractedOrganization",
            Text(language=TextLanguage.DE, value="Beispiel Text"),
        ),
        (
            EditorValue(text="VALID_FOR_PROCESSING", badge="ConsentStatus"),
            "hasConsentType",
            "MergedConsent",
            ConsentStatus["VALID_FOR_PROCESSING"],
        ),
        (
            EditorValue(text="2004", badge="year"),
            "start",
            "ExtractedActivity",
            Year(2004),
        ),
        (
            EditorValue(text="Funds for Funding e.V."),
            "fundingProgram",
            "ExtractedActivity",
            "Funds for Funding e.V.",
        ),
    ],
    ids=["link", "text", "vocab", "temporal", "string"],
)
def test_transform_render_value_to_model_type(
    editor_value: EditorValue, field_name: str, class_name: str, expected: object
) -> None:
    model_value = _transform_editor_value_to_model_value(
        editor_value,
        field_name,
        class_name,
    )
    assert model_value == expected


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (
            EditorField(
                name="unknownField",
                primary_sources=[
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 1"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource001"),
                    )
                ],
            ),
            {},
        ),
        (
            EditorField(
                name="familyName",
                primary_sources=[
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 1"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource001"),
                        editor_values=[
                            EditorValue(text="active", enabled=True),
                            EditorValue(text="inactive", enabled=False),
                        ],
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 2"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        editor_values=[
                            EditorValue(text="another inactive", enabled=False),
                        ],
                    ),
                ],
            ),
            {"familyName": ["inactive", "another inactive"]},
        ),
    ],
)
def test_transform_field_to_subtractive(
    field: EditorField, expected: dict[str, object]
) -> None:
    subtractive = SubtractivePerson()
    _transform_field_to_subtractive(field, subtractive)
    assert subtractive.model_dump(exclude_defaults=True) == expected


def test_transform_fields_to_rule_set() -> None:
    rule_set_request = transform_fields_to_rule_set(
        "Person",
        [
            EditorField(
                name="givenName",
                primary_sources=[
                    EditorPrimarySource(
                        name=EditorValue(text="Enabled Primary Source"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource001"),
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Prevented Primary Source"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        enabled=False,
                    ),
                ],
            ),
            EditorField(
                name="familyName",
                primary_sources=[
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 1"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource001"),
                        editor_values=[
                            EditorValue(text="active", enabled=True),
                            EditorValue(text="inactive", enabled=False),
                        ],
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 2"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        editor_values=[
                            EditorValue(text="another inactive", enabled=False),
                        ],
                    ),
                ],
            ),
        ],
    )
    assert rule_set_request.entityType == "PersonRuleSetRequest"
    assert rule_set_request.model_dump(exclude_defaults=True) == {
        "subtractive": {
            "familyName": ["inactive", "another inactive"],
        },
        "preventive": {
            "givenName": ["PrimarySource002"],
        },
    }
