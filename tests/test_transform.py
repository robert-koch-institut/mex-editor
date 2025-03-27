import pytest

from mex.common.exceptions import MExError
from mex.common.models import AnyExtractedModel
from mex.common.types import APIType, Identifier, Link, LinkLanguage, Text, TextLanguage
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_stem_type,
    transform_models_to_title,
    transform_value,
    transform_values,
)


@pytest.mark.parametrize(
    ("values", "allow_link", "expected"),
    [
        (None, True, []),
        (
            "foo",
            True,
            [EditorValue(text="foo", display_text="foo", resolved=True)],
        ),
        (
            [
                "bar",
                APIType["REST"],
                Text(value="hi there", language=TextLanguage.EN),
                Link(url="http://mex", title="homepage", language=LinkLanguage.EN),
            ],
            True,
            [
                EditorValue(text="bar", display_text="bar", resolved=True),
                EditorValue(
                    text="REST", display_text="REST", badge="APIType", resolved=True
                ),
                EditorValue(
                    text="hi there",
                    display_text="hi there",
                    badge="en",
                    resolved=True,
                ),
                EditorValue(
                    text="homepage",
                    display_text="homepage",
                    badge="en",
                    href="http://mex",
                    external=True,
                    resolved=True,
                ),
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            True,
            [
                EditorValue(
                    text="cWWm02l1c6cucKjIhkFqY4",
                    display_text="cWWm02l1c6cucKjIhkFqY4",
                    href="/item/cWWm02l1c6cucKjIhkFqY4",
                    is_identifier=True,
                    resolved=False,
                )
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            False,
            [
                EditorValue(
                    text="cWWm02l1c6cucKjIhkFqY4",
                    display_text="cWWm02l1c6cucKjIhkFqY4",
                    is_identifier=True,
                    resolved=False,
                )
            ],
        ),
    ],
)
def test_transform_values(
    values: object, allow_link: bool, expected: list[EditorValue]
) -> None:
    assert transform_values(values, allow_link=allow_link) == expected


def test_transform_value_none_error() -> None:
    with pytest.raises(MExError, match="cannot transform NoneType to editor value"):
        transform_value(None)


def test_transform_models_to_stem_type_empty() -> None:
    assert transform_models_to_stem_type([]) is None


def test_transform_models_to_stem_type(dummy_data: list[AnyExtractedModel]) -> None:
    assert transform_models_to_stem_type(dummy_data[:2]) == "PrimarySource"


def test_transform_models_to_title_empty() -> None:
    assert transform_models_to_title([]) == []


def test_transform_models_to_title(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_titles = [transform_models_to_title([d]) for d in dummy_data]
    assert dummy_titles == [
        [
            # ps-1 primary source renders title as text
            EditorValue(
                text="Primary Source One",
                display_text="Primary Source One",
                badge="en",
                resolved=True,
            )
        ],
        [
            # ps-2 primary source renders title as text
            EditorValue(
                text="Primary Source Two",
                display_text="Primary Source Two",
                badge="en",
                resolved=True,
            )
        ],
        [
            # contact-point renders email as text
            EditorValue(
                text="info@contact-point.one",
                display_text="info@contact-point.one",
                resolved=True,
            )
        ],
        [
            # contact-point renders email as text
            EditorValue(
                text="help@contact-point.two",
                display_text="help@contact-point.two",
                resolved=True,
            )
        ],
        [
            # unit renders shortName as text (no language badge)
            EditorValue(text="OU1", display_text="OU1", resolved=True)
        ],
        [
            # activity renders title as text (with language badge)
            EditorValue(
                text="Aktivität 1",
                display_text="Aktivität 1",
                badge="de",
                resolved=True,
            )
        ],
    ]


def test_transform_models_to_preview_empty() -> None:
    assert transform_models_to_preview([]) == []


def test_transform_models_to_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [transform_models_to_preview([d]) for d in dummy_data]
    assert dummy_previews == [
        [
            EditorValue(
                text="PrimarySource", display_text="PrimarySource", resolved=True
            )
        ],
        [
            EditorValue(
                text="PrimarySource", display_text="PrimarySource", resolved=True
            )
        ],
        [EditorValue(text="ContactPoint", display_text="ContactPoint", resolved=True)],
        [EditorValue(text="ContactPoint", display_text="ContactPoint", resolved=True)],
        [
            EditorValue(
                text="Unit 1",
                display_text="Unit 1",
                badge="en",
                enabled=True,
                resolved=True,
            )
        ],
        [
            EditorValue(text="A1", display_text="A1", enabled=True, resolved=True),
            EditorValue(
                text="wEvxYRPlmGVQCbZx9GAbn",
                display_text="wEvxYRPlmGVQCbZx9GAbn",
                is_identifier=True,
            ),
            EditorValue(
                text="g32qzYNVH1Ez7JTEk3fvLF",
                display_text="g32qzYNVH1Ez7JTEk3fvLF",
                is_identifier=True,
            ),
            EditorValue(
                text="cWWm02l1c6cucKjIhkFqY4",
                display_text="cWWm02l1c6cucKjIhkFqY4",
                is_identifier=True,
            ),
            EditorValue(
                text="cWWm02l1c6cucKjIhkFqY4",
                display_text="cWWm02l1c6cucKjIhkFqY4",
                is_identifier=True,
            ),
            EditorValue(
                text="1999-12-24",
                display_text="1999-12-24",
                badge="day",
                resolved=True,
            ),
            EditorValue(
                text="2023-01-01",
                display_text="2023-01-01",
                badge="day",
                resolved=True,
            ),
        ],
    ]
