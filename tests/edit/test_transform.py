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
    PreventivePerson,
    SubtractiveActivity,
    SubtractiveConsent,
    SubtractivePerson,
)
from mex.common.types import (
    ConsentStatus,
    ConsentType,
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
from mex.editor.edit.models import EditorField, EditorPrimarySource, InputConfig
from mex.editor.edit.transform import (
    _get_primary_source_id_from_model,
    _transform_editor_value_to_model_value,
    _transform_fields_to_additive,
    _transform_fields_to_preventive,
    _transform_fields_to_subtractive,
    _transform_model_to_additive_input_config,
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


def test_get_primary_source_id_from_model_error() -> None:
    with pytest.raises(RuntimeError, match="Cannot get primary source ID for model"):
        _get_primary_source_id_from_model(Text(value="won't work"))


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
            [EditorValue(text="ConsentStatus", badge="VALID_FOR_PROCESSING")],
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
                    badge="EN",
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
        "entity_type",
        "field_name",
        "expected",
    ),
    [
        ("AdditiveActivity", "fundingProgram", InputConfig(editable_text=True)),
        ("AdditiveResource", "created", InputConfig(editable_text=True)),
        ("AdditiveContactPoint", "email", InputConfig(editable_text=True)),
        ("AdditivePerson", "affiliation", InputConfig()),
        (
            "AdditiveResource",
            "license",
            InputConfig(
                badge_default="CREATIVE_COMMONS_ATTRIBUTION_INTERNATIONAL",
                badge_options=["CREATIVE_COMMONS_ATTRIBUTION_INTERNATIONAL"],
                badge_titles=["License"],
                editable_href=False,
                editable_badge=True,
                editable_text=False,
            ),
        ),
        (
            "AdditiveResource",
            "documentation",
            InputConfig(
                badge_options=["DE", "EN"],
                badge_default="DE",
                badge_titles=["LinkLanguage"],
                editable_href=True,
                editable_badge=True,
                editable_text=True,
            ),
        ),
        (
            "AdditiveResource",
            "keyword",
            InputConfig(
                badge_options=["DE", "EN"],
                badge_default="DE",
                badge_titles=["TextLanguage"],
                editable_badge=True,
                editable_text=True,
            ),
        ),
        ("AdditiveResource", "minTypicalAge", InputConfig()),
        ("AdditiveResource", "unknown", InputConfig()),
    ],
    ids=[
        "string field",
        "temporal field",
        "email field",  # stopgap: MX-1766
        "reference field",  # stopgap: MX-1652
        "vocabulary field",
        "link field",  # stopgap: MX-1650
        "text field",  # stopgap: MX-1650
        "integer field",  # stopgap: MX-1793
        "unknown field",
    ],
)
def test_transform_model_to_additive_input_config(
    entity_type: str,
    field_name: str,
    expected: InputConfig,
) -> None:
    input_config = _transform_model_to_additive_input_config(
        field_name, entity_type, True
    )
    assert input_config == expected


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
                    input_config=InputConfig(),
                    enabled=True,
                )
            ],
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId", href="/item/primarySourceId"
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    input_config=InputConfig(),
                    enabled=True,
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
                    input_config=InputConfig(),
                    enabled=True,
                )
            ],
            [
                EditorPrimarySource(
                    name=EditorValue(
                        text="primarySourceId",
                        href="/item/primarySourceId",
                    ),
                    identifier=MergedPrimarySourceIdentifier("primarySourceId"),
                    editor_values=[EditorValue(text="Family")],
                    enabled=False,
                    input_config=InputConfig(),
                )
            ],
        ),
    ],
    ids=["without rules", "with rules"],
)
def test_transform_model_to_editor_primary_sources(
    model: AnyExtractedModel | AnyAdditiveModel,
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
            ExtractedPerson(
                email=["person000@rki.de"],
                hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
                identifierInPrimarySource="person-000",
            )
        ],
        additive=AdditivePerson(givenName=["Good"]),
        subtractive=SubtractivePerson(givenName=["Bad"]),
        preventive=PreventivePerson(memberOf=[MEX_PRIMARY_SOURCE_STABLE_TARGET_ID]),
    )

    assert len(editor_fields) == len(MERGEABLE_FIELDS_BY_CLASS_NAME["MergedPerson"])
    fields_by_name = {f.name: f for f in editor_fields}
    assert fields_by_name["givenName"].dict() == {
        "name": "givenName",
        "primary_sources": [
            {
                "name": {
                    "text": "00000000000000",
                    "badge": None,
                    "href": "/item/00000000000000",
                    "external": False,
                    "enabled": True,
                },
                "identifier": "00000000000000",
                "input_config": {
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_href": False,
                    "editable_badge": False,
                    "editable_text": False,
                },
                "editor_values": [],
                "enabled": True,
            },
            {
                "name": {
                    "text": "00000000000000",
                    "badge": None,
                    "href": "/item/00000000000000",
                    "external": False,
                    "enabled": True,
                },
                "identifier": "00000000000000",
                "input_config": {
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_href": False,
                    "editable_badge": False,
                    "editable_text": True,
                },
                "editor_values": [
                    {
                        "text": "Good",
                        "badge": None,
                        "href": None,
                        "external": False,
                        "enabled": True,
                    }
                ],
                "enabled": True,
            },
        ],
    }
    assert fields_by_name["memberOf"].dict() == {
        "name": "memberOf",
        "primary_sources": [
            {
                "name": {
                    "text": "00000000000000",
                    "badge": None,
                    "href": "/item/00000000000000",
                    "external": False,
                    "enabled": True,
                },
                "identifier": "00000000000000",
                "input_config": {
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_href": False,
                    "editable_badge": False,
                    "editable_text": False,
                },
                "editor_values": [],
                "enabled": False,
            },
            {
                "name": {
                    "text": "00000000000000",
                    "badge": None,
                    "href": "/item/00000000000000",
                    "external": False,
                    "enabled": True,
                },
                "identifier": "00000000000000",
                "input_config": {
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_href": False,
                    "editable_badge": False,
                    "editable_text": False,
                },
                "editor_values": [],
                "enabled": False,
            },
        ],
    }


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (
            EditorField(
                name="unknownField",
                primary_sources=[
                    EditorPrimarySource(
                        enabled=True,
                        input_config=InputConfig(),
                        name=EditorValue(text="No Input Config"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource000000"),
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
                        input_config=InputConfig(editable_text=True),
                        name=EditorValue(text="PS2"),
                        identifier=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
                        editor_values=[
                            EditorValue(text="Duplicate"),
                            EditorValue(text="Duplicate"),
                        ],
                    ),
                ],
            ),
            {"familyName": ["Duplicate"]},
        ),
    ],
)
def test_transform_fields_to_additive(
    field: EditorField, expected: dict[str, object]
) -> None:
    additive = _transform_fields_to_additive([field], "Person")
    assert additive == expected


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (
            EditorField(
                name="unknownField",
                primary_sources=[
                    EditorPrimarySource(
                        enabled=True,
                        input_config=InputConfig(),
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
                        input_config=InputConfig(),
                        name=EditorValue(text="Enabled Primary Source"),
                        identifier=MergedPrimarySourceIdentifier(
                            "enabledPrimarySourceId"
                        ),
                    ),
                    EditorPrimarySource(
                        enabled=False,
                        input_config=InputConfig(),
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
def test_transform_fields_to_preventive(
    field: EditorField, expected: dict[str, object]
) -> None:
    preventive = _transform_fields_to_preventive([field], "Person")
    assert preventive == expected


@pytest.mark.parametrize(
    ("editor_value", "field_name", "class_name", "expected"),
    [
        (
            EditorValue(text="Titel", badge="DE", href="https://beispiel"),
            "documentation",
            "AdditiveResource",
            Link(url="https://beispiel", language=LinkLanguage.DE, title="Titel"),
        ),
        (
            EditorValue(text="Beispiel Text", badge="DE"),
            "alternativeName",
            "AdditiveOrganization",
            Text(language=TextLanguage.DE, value="Beispiel Text"),
        ),
        (
            EditorValue(text="EXPRESSED_CONSENT", badge="ConsentStatus"),
            "hasConsentType",
            "AdditiveConsent",
            ConsentType["EXPRESSED_CONSENT"],
        ),
        (
            EditorValue(),
            "hasConsentType",
            "AdditiveConsent",
            ConsentType["IMPLIED_CONSENT"],
        ),
        (
            EditorValue(text="2004", badge="year"),
            "start",
            "AdditiveActivity",
            Year(2004),
        ),
        (
            EditorValue(text="Funds for Funding e.V."),
            "fundingProgram",
            "AdditiveActivity",
            "Funds for Funding e.V.",
        ),
    ],
    ids=["link", "text", "vocab", "default vocab", "temporal", "string"],
)
def test_transform_editor_value_to_model_value(
    editor_value: EditorValue, field_name: str, class_name: str, expected: object
) -> None:
    input_config = _transform_model_to_additive_input_config(
        field_name, class_name, True
    )
    assert input_config

    model_value = _transform_editor_value_to_model_value(
        editor_value,
        field_name,
        class_name,
        input_config,
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
                        input_config=InputConfig(),
                        enabled=True,
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
                        input_config=InputConfig(),
                        enabled=True,
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 2"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        editor_values=[
                            EditorValue(text="inactive", enabled=False),
                            EditorValue(text="another inactive", enabled=False),
                        ],
                        input_config=InputConfig(),
                        enabled=True,
                    ),
                ],
            ),
            {"familyName": ["inactive", "another inactive"]},
        ),
    ],
)
def test_transform_fields_to_subtractive(
    field: EditorField, expected: dict[str, object]
) -> None:
    subtractive = _transform_fields_to_subtractive([field], "Person")
    assert subtractive == expected


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
                        input_config=InputConfig(),
                        enabled=True,
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Prevented Primary Source"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        enabled=False,
                        input_config=InputConfig(),
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
                        input_config=InputConfig(),
                        enabled=True,
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 2"),
                        identifier=MergedPrimarySourceIdentifier("PrimarySource002"),
                        editor_values=[
                            EditorValue(text="another inactive", enabled=False),
                        ],
                        input_config=InputConfig(),
                        enabled=True,
                    ),
                    EditorPrimarySource(
                        name=EditorValue(text="Primary Source 3"),
                        identifier=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
                        editor_values=[
                            EditorValue(text="SomeName", enabled=True),
                        ],
                        input_config=InputConfig(editable_text=True),
                        enabled=True,
                    ),
                ],
            ),
        ],
    )
    assert rule_set_request.entityType == "PersonRuleSetRequest"
    assert rule_set_request.model_dump(exclude_defaults=True) == {
        "additive": {
            "familyName": ["SomeName"],
        },
        "subtractive": {
            "familyName": ["inactive", "another inactive"],
        },
        "preventive": {
            "givenName": ["PrimarySource002"],
        },
    }
