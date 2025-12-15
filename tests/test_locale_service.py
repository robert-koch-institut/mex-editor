import pytest

from mex.editor.locale_service import LocaleService, camelcase_to_title


@pytest.mark.parametrize(
    ("input_camelcase", "expected"),
    [
        ("", ""),
        ("simplestring", "Simplestring"),
        ("inputCamelCase", "Input Camel Case"),
        (
            "a bit_weired string_that might be _work _for_some_reason_",
            "A Bit_Weired String_That Might Be _Work _For_Some_Reason_",
        ),
    ],
    ids=["emtpy string", "simple string", "simple camelcase", "weired camelcase"],
)
def test_camelcase_to_title(input_camelcase: str, expected: str) -> None:
    assert camelcase_to_title(input_camelcase) == expected


@pytest.mark.parametrize(
    ("locale_id", "stem_type", "field_name", "pluralize", "expected_label"),
    [
        pytest.param(
            "de-DE",
            "Resource",
            "conformsTo",
            False,
            "Standard",
            id="de-DE:Resource.conformsTo(singular)",
        ),
        pytest.param(
            "de-DE",
            "Resource",
            "conformsTo",
            True,
            "Standards",
            id="de-DE:Resource.conformsTo(plural)",
        ),
        pytest.param(
            "en-US",
            "Resource",
            "conformsTo",
            False,
            "Standard",
            id="en-US:Resource.conformsTo(singular)",
        ),
        pytest.param(
            "en-US",
            "Resource",
            "conformsTo",
            True,
            "Standards",
            id="en-US:Resource.conformsTo(plural)",
        ),
        pytest.param(
            "de-DE",
            "Resource",
            "contributor",
            False,
            "Mitwirkende-DE*r",
            id="de-DE:Resource.contributor(singular)",
        ),
        pytest.param(
            "de-DE",
            "Resource",
            "contributor",
            True,
            "Mitwirkende-DE",
            id="de-DE:Resource.contributor(plural)",
        ),
        pytest.param(
            "en-US",
            "Resource",
            "contributor",
            False,
            "Contributor",
            id="en-US:Resource.contributor(singular)",
        ),
        pytest.param(
            "en-US",
            "Resource",
            "contributor",
            True,
            "Contributors",
            id="en-US:Resource.contributor(plural)",
        ),
        pytest.param(
            "de-DE",
            "Variable",
            "dataType",
            False,
            "Datentyp",
            id="de-DE:Variable.dataType(singular)",
        ),
        pytest.param(
            "de-DE",
            "Variable",
            "dataType",
            True,
            "Datentyp",
            id="de-DE:Variable.dataType(plural)",
        ),
        pytest.param(
            "en-US",
            "Variable",
            "dataType",
            False,
            "Data type",
            id="en-US:Variable.dataType(singular)",
        ),
        pytest.param(
            "en-US",
            "Variable",
            "dataType",
            True,
            "Data type",
            id="en-US:Variable.dataType(plural)",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "abstract",
            False,
            "Kurzbeschreibung",
            id="de-DE:AnyStemType.abstract(singular)",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "abstract",
            True,
            "Kurzbeschreibung",
            id="de-DE:AnyStemType.abstract(plural)",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "abstract",
            False,
            "Abstract",
            id="en-US:AnyStemType.abstract(singular)",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "abstract",
            True,
            "Abstract",
            id="en-US:AnyStemType.abstract(plural)",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "alternativeTitle",
            False,
            "Alternativtitel",
            id="de-DE:AnyStemType.alternativeTitle(singular)",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "alternativeTitle",
            True,
            "Alternative Titel",
            id="de-DE:AnyStemType.alternativeTitle(plural)",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "alternativeTitle",
            False,
            "Alternative title",
            id="en-US:AnyStemType.alternativeTitle(singular)",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "alternativeTitle",
            True,
            "Alternative titles",
            id="en-US:AnyStemType.alternativeTitle(plural)",
        ),
        pytest.param(
            "de-DE",
            "UnknownStemType",
            "unknownField",
            False,
            "Unknown Field",
            id="de-DE:UnknownStemType.unknownField(singular)",
        ),
        pytest.param(
            "de-DE",
            "UnknownStemType",
            "unknownField",
            True,
            "Unknown Field",
            id="de-DE:UnknownStemType.unknownField(plural)",
        ),
        pytest.param(
            "de-DE",
            "UnknownStemType",
            "unknownField",
            False,
            "Unknown Field",
            id="en-US:UnknownStemType.unknownField(singular)",
        ),
        pytest.param(
            "en-US",
            "UnknownStemType",
            "unknownField",
            True,
            "Unknown Field",
            id="en-US:UnknownStemType.unknownField(plural)",
        ),
    ],
)
def test_get_field_label(
    locale_id: str,
    stem_type: str,
    field_name: str,
    pluralize: bool,  # noqa: FBT001
    expected_label: str,
) -> None:
    locale_service = LocaleService.get()
    assert (
        locale_service.get_field_label(
            locale_id, stem_type, field_name, 2 if pluralize else 1
        )
        == expected_label
    )


@pytest.mark.parametrize(
    ("locale_id", "stem_type", "field_name", "expected_description"),
    [
        pytest.param(
            "de-DE",
            "Activity",
            "abstract",
            "Kurze Beschreibung des Kontexts, in dem die Daten verarbeitet wurden",
            id="de-DE:Activity.abstract",
        ),
        pytest.param(
            "en-US",
            "Activity",
            "abstract",
            "Brief description of the context in which the data was processed",
            id="en-US:Activity.abstract",
        ),
        pytest.param(
            "de-DE",
            "Resource",
            "accessPlatform",
            "Zugriffsplattform für die Daten",
            id="de-DE:Resource.accessPlatform",
        ),
        pytest.param(
            "en-US",
            "Resource",
            "accessPlatform",
            "Access platform for the data",
            id="en-US:Resource.accessPlatform",
        ),
        pytest.param(
            "de-DE",
            "Person",
            "affiliation",
            "Institution, zu der die Person zugehörig ist",
            id="de-DE:Person.affiliation",
        ),
        pytest.param(
            "en-US",
            "Person",
            "affiliation",
            "Institution to which the person belongs",
            id="en-US:Person.affiliation",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "alternativeTitle",
            "Andere(r) Titel",
            id="de-DE:AnyStemType.alternativeTitle",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "alternativeTitle",
            "Other title(s)",
            id="en-US:AnyStemType.alternativeTitle",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "identifier",
            "Alle extrahierten Metadatenobjekte werden mit einem Identifikator versehen",
            id="de-DE:AnyStemType.identifier",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "identifier",
            "All extracted metadata objects are provided with an identifier",
            id="en-US:AnyStemType.identifier",
        ),
        pytest.param(
            "de-DE",
            "AnyStemType",
            "unknownField",
            "",
            id="de-DE:AnyStemType.unknownField",
        ),
        pytest.param(
            "en-US",
            "AnyStemType",
            "unknownField",
            "",
            id="en-US:AnyStemType.unknownField",
        ),
    ],
)
def test_get_field_description(
    locale_id: str,
    stem_type: str,
    field_name: str,
    expected_description: str,
) -> None:
    locale_service = LocaleService.get()
    assert (
        locale_service.get_field_description(locale_id, stem_type, field_name)
        == expected_description
    )
