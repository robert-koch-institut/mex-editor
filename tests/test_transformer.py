import polib
import pytest

from mex.editor.transformer import (
    DuplicateKeyError,
    transform_pofile_to_message_format_json,
)


@pytest.mark.parametrize(
    ("pofile_content", "expected_json"),
    [
        (
            """msgctxt "Resource"
msgid "accessPlatform.singular"
msgid_plural "accessPlatform.plural"
msgstr[0] "Zugriffsplattform"
msgstr[1] "Zugriffsplattformen"

msgctxt "Resource"
msgid "accessPlatform.description"
msgstr "Zugriffsplattform für die Daten"

msgid "accessRestriction.singular"
msgstr "Zugriffsbeschränkung" """,
            {
                "Resource.accessPlatform": "{count, plural, one {Zugriffsplattform} other {Zugriffsplattformen}}",
                "Resource.accessPlatform.description": "Zugriffsplattform für die Daten",
                "accessRestriction": "Zugriffsbeschränkung",
            },
        )
    ],
)
def test_transform_pofile_to_message_format_json(
    pofile_content: str, expected_json: dict[str, str]
) -> None:
    po = polib.pofile(pofile_content)
    assert transform_pofile_to_message_format_json(po) == expected_json


@pytest.mark.parametrize(
    ("pofile_content"),
    [
        (
            """msgctxt "Resource"
msgid "accessPlatform.singular"
msgid_plural "accessPlatform.plural"
msgstr[0] "Zugriffsplattform"
msgstr[1] "Zugriffsplattformen"

msgid "Resource.accessPlatform"
msgstr "Zugriffsplattform für die Daten" """
        )
    ],
)
def test_transform_pofile_to_message_format_json_duplicate_key(
    pofile_content: str,
) -> None:
    po = polib.pofile(pofile_content)
    with pytest.raises(DuplicateKeyError):
        transform_pofile_to_message_format_json(po)
