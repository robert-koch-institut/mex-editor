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
    ("locale", "stem_type", "field_name", "pluralize", "expected_label"),
    [
        ("de-DE", "Resource", "conformsTo", False, "Standard"),
        ("de-DE", "Resource", "conformsTo", True, "Standards"),
        ("en-US", "Resource", "conformsTo", False, "Standard"),
        ("en-US", "Resource", "conformsTo", True, "Standards"),
        ("de-DE", "Resource", "contributor", False, "Mitwirkende*r"),
        ("de-DE", "Resource", "contributor", True, "Mitwirkende"),
        ("en-US", "Resource", "contributor", False, "Contributor"),
        ("en-US", "Resource", "contributor", True, "Contributors"),
        ("de-DE", "Variable", "dataType", False, "Datentyp"),
        ("de-DE", "Variable", "dataType", True, "Datentyp"),
        ("en-US", "Variable", "dataType", False, "Data type"),
        ("en-US", "Variable", "dataType", True, "Data type"),
        ("de-DE", "AnyStemType", "abstract", False, "Kurzbeschreibung"),
        ("de-DE", "AnyStemType", "abstract", True, "Kurzbeschreibung"),
        ("en-US", "AnyStemType", "abstract", False, "Abstract"),
        ("en-US", "AnyStemType", "abstract", True, "Abstract"),
        ("de-DE", "AnyStemType", "alternativeTitle", False, "Alternativtitel"),
        ("de-DE", "AnyStemType", "alternativeTitle", True, "Alternative Titel"),
        ("en-US", "AnyStemType", "alternativeTitle", False, "Alternative title"),
        ("en-US", "AnyStemType", "alternativeTitle", True, "Alternative titles"),
        ("de-DE", "UnknownStemType", "unknownField", False, "Unknown Field"),
        ("de-DE", "UnknownStemType", "unknownField", True, "Unknown Field"),
        ("en-US", "UnknownStemType", "unknownField", False, "Unknown Field"),
        ("en-US", "UnknownStemType", "unknownField", True, "Unknown Field"),
    ],
    ids=[
        "de:Resource.conformsTo(singular)",
        "de:Resource.conformsTo(pluaral)",
        "en:Resource.conformsTo(singular)",
        "en:Resource.conformsTo(pluaral)",
        "de:Resource.contributor(singular)",
        "de:Resource.contributor(pluaral)",
        "en:Resource.contributor(singular)",
        "en:Resource.contributor(pluaral)",
        "de:Variable.dataType(singular)",
        "de:Variable.dataType(pluaral)",
        "en:Variable.dataType(singular)",
        "en:Variable.dataType(pluaral)",
        "de:AnyStemType.abstract(singular)",
        "de:AnyStemType.abstract(pluaral)",
        "en:AnyStemType.abstract(singular)",
        "en:AnyStemType.abstract(pluaral)",
        "de:AnyStemType.alternativeTitle(singular)",
        "de:AnyStemType.alternativeTitle(pluaral)",
        "en:AnyStemType.alternativeTitle(singular)",
        "en:AnyStemType.alternativeTitle(pluaral)",
        "de:UnknownStemType.unknownField(singular)",
        "de:UnknownStemType.unknownField(pluaral)",
        "en:UnknownStemType.unknownField(singular)",
        "en:UnknownStemType.unknownField(pluaral)",
    ],
)
def test_get_field_label(
    locale: str,
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
        (
            "de-DE",
            "Activity",
            "abstract",
            "Kurze Beschreibung des Kontexts, in dem die Daten verarbeitet wurden",
        ),
        (
            "en-US",
            "Activity",
            "abstract",
            "Brief description of the context in which the data was processed",
        ),
        ("de-DE", "Resource", "accessPlatform", "Zugriffsplattform für die Daten"),
        ("en-US", "Resource", "accessPlatform", "Access platform for the data"),
        (
            "de-DE",
            "Person",
            "affiliation",
            "Institution, zu der die Person zugehörig ist",
        ),
        ("en-US", "Person", "affiliation", "Institution to which the person belongs"),
        ("de-DE", "AnyStemType", "alternativeTitle", "Andere(r) Titel"),
        ("en-US", "AnyStemType", "alternativeTitle", "Other title(s)"),
        (
            "de-DE",
            "AnyStemType",
            "identifier",
            "Alle extrahierten Metadatenobjekte werden mit einem Identifikator versehen",
        ),
        (
            "en-US",
            "AnyStemType",
            "identifier",
            "All extracted metadata objects are provided with an identifier",
        ),
    ],
    ids=[
        "de:Activity.abstract",
        "en:Activity.abstract",
        "de:Resource.accessPlatform",
        "en:Resource.accessPlatform",
        "de:Person.affiliation",
        "en:Person.affiliation",
        "de:AnyStemType.alternativeTitle",
        "en:AnyStemType.alternativeTitle",
        "de:AnyStemType.identifier",
        "en:AnyStemType.identifier",
    ],
)
def test_get_field_description(
    locale: str,
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
