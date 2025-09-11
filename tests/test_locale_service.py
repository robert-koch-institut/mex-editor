import pytest

from mex.editor.locale_service import LocaleService, MexLocale, camelcase_to_title


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
    ("locale", "stem_type", "field_name", "pluralize", "expected_label"),
    [
        pytest.param(
            MexLocale.DE,
            "Resource",
            "conformsTo",
            False,
            "Standard",
            id="de:Resource.conformsTo(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "Resource",
            "conformsTo",
            True,
            "Standards",
            id="de:Resource.conformsTo(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "Resource",
            "conformsTo",
            False,
            "Standard",
            id="en:Resource.conformsTo(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "Resource",
            "conformsTo",
            True,
            "Standards",
            id="en:Resource.conformsTo(plural)",
        ),
        pytest.param(
            MexLocale.DE,
            "Resource",
            "contributor",
            False,
            "Mitwirkende*r",
            id="de:Resource.contributor(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "Resource",
            "contributor",
            True,
            "Mitwirkende",
            id="de:Resource.contributor(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "Resource",
            "contributor",
            False,
            "Contributor",
            id="en:Resource.contributor(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "Resource",
            "contributor",
            True,
            "Contributors",
            id="en:Resource.contributor(plural)",
        ),
        pytest.param(
            MexLocale.DE,
            "Variable",
            "dataType",
            False,
            "Datentyp",
            id="de:Variable.dataType(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "Variable",
            "dataType",
            True,
            "Datentyp",
            id="de:Variable.dataType(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "Variable",
            "dataType",
            False,
            "Data type",
            id="en:Variable.dataType(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "Variable",
            "dataType",
            True,
            "Data type",
            id="en:Variable.dataType(plural)",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "abstract",
            False,
            "Kurzbeschreibung",
            id="de:AnyStemType.abstract(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "abstract",
            True,
            "Kurzbeschreibung",
            id="de:AnyStemType.abstract(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "abstract",
            False,
            "Abstract",
            id="en:AnyStemType.abstract(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "abstract",
            True,
            "Abstract",
            id="en:AnyStemType.abstract(plural)",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "alternativeTitle",
            False,
            "Alternativtitel",
            id="de:AnyStemType.alternativeTitle(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "alternativeTitle",
            True,
            "Alternative Titel",
            id="de:AnyStemType.alternativeTitle(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "alternativeTitle",
            False,
            "Alternative title",
            id="en:AnyStemType.alternativeTitle(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "alternativeTitle",
            True,
            "Alternative titles",
            id="en:AnyStemType.alternativeTitle(plural)",
        ),
        pytest.param(
            MexLocale.DE,
            "UnknownStemType",
            "unknownField",
            False,
            "Unknown Field",
            id="de:UnknownStemType.unknownField(singular)",
        ),
        pytest.param(
            MexLocale.DE,
            "UnknownStemType",
            "unknownField",
            True,
            "Unknown Field",
            id="de:UnknownStemType.unknownField(plural)",
        ),
        pytest.param(
            MexLocale.EN,
            "UnknownStemType",
            "unknownField",
            False,
            "Unknown Field",
            id="en:UnknownStemType.unknownField(singular)",
        ),
        pytest.param(
            MexLocale.EN,
            "UnknownStemType",
            "unknownField",
            True,
            "Unknown Field",
            id="en:UnknownStemType.unknownField(plural)",
        ),
    ],
)
def test_get_field_label(
    locale: MexLocale,
    stem_type: str,
    field_name: str,
    pluralize: bool,  # noqa: FBT001
    expected_label: str,
) -> None:
    locale_service = LocaleService.get()
    locale_service.set_locale(locale)
    assert (
        locale_service.get_field_label(stem_type, field_name, 2 if pluralize else 1)
        == expected_label
    )


@pytest.mark.parametrize(
    ("locale", "stem_type", "field_name", "expected_description"),
    [
        pytest.param(
            MexLocale.DE,
            "Activity",
            "abstract",
            "Kurze Beschreibung des Kontexts, in dem die Daten verarbeitet wurden",
            id="de:Activity.abstract",
        ),
        pytest.param(
            MexLocale.EN,
            "Activity",
            "abstract",
            "Brief description of the context in which the data was processed",
            id="en:Activity.abstract",
        ),
        pytest.param(
            MexLocale.DE,
            "Resource",
            "accessPlatform",
            "Zugriffsplattform für die Daten",
            id="de:Resource.accessPlatform",
        ),
        pytest.param(
            MexLocale.EN,
            "Resource",
            "accessPlatform",
            "Access platform for the data",
            id="en:Resource.accessPlatform",
        ),
        pytest.param(
            MexLocale.DE,
            "Person",
            "affiliation",
            "Institution, zu der die Person zugehörig ist",
            id="de:Person.affiliation",
        ),
        pytest.param(
            MexLocale.EN,
            "Person",
            "affiliation",
            "Institution to which the person belongs",
            id="en:Person.affiliation",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "alternativeTitle",
            "Andere(r) Titel",
            id="de:AnyStemType.alternativeTitle",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "alternativeTitle",
            "Other title(s)",
            id="en:AnyStemType.alternativeTitle",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "identifier",
            "Alle extrahierten Metadatenobjekte werden mit einem Identifikator versehen",
            id="de:AnyStemType.identifier",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "identifier",
            "All extracted metadata objects are provided with an identifier",
            id="en:AnyStemType.identifier",
        ),
        pytest.param(
            MexLocale.DE,
            "AnyStemType",
            "unknownField",
            "",
            id="de:AnyStemType.unknownField",
        ),
        pytest.param(
            MexLocale.EN,
            "AnyStemType",
            "unknownField",
            "",
            id="en:AnyStemType.unknownField",
        ),
    ],
)
def test_get_field_description(
    locale: MexLocale,
    stem_type: str,
    field_name: str,
    expected_description: str,
) -> None:
    locale_service = LocaleService.get()
    locale_service.set_locale(locale)
    assert (
        locale_service.get_field_description(stem_type, field_name)
        == expected_description
    )
