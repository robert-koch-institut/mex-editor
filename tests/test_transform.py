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
            [EditorValue(text="foo")],
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
                EditorValue(text="bar"),
                EditorValue(text="REST", badge="APIType"),
                EditorValue(text="hi there", badge="en"),
                EditorValue(
                    text="homepage", badge="en", href="http://mex", external=True
                ),
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            True,
            [
                EditorValue(
                    text="cWWm02l1c6cucKjIhkFqY4", href="/item/cWWm02l1c6cucKjIhkFqY4"
                )
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            False,
            [EditorValue(text="cWWm02l1c6cucKjIhkFqY4")],
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
            # mex primary source has no title, renders type instead
            EditorValue(text="PrimarySource")
        ],
        [
            # ps-2 primary source has no title either
            EditorValue(text="PrimarySource")
        ],
        [
            # contact-point renders email as text
            EditorValue(text="info@contact-point.one")
        ],
        [
            # contact-point renders email as text
            EditorValue(text="help@contact-point.two")
        ],
        [
            # unit renders shortName as text (no language badge)
            EditorValue(text="OU1")
        ],
        [
            # activity renders title as text (with language badge)
            EditorValue(text="Aktivität 1", badge="de")
        ],
    ]


def test_transform_models_to_preview_empty() -> None:
    assert transform_models_to_preview([]) == []


def test_transform_models_to_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [transform_models_to_preview([d]) for d in dummy_data]
    assert dummy_previews == [
        [EditorValue(text="PrimarySource")],
        [EditorValue(text="PrimarySource")],
        [EditorValue(text="ContactPoint")],
        [EditorValue(text="ContactPoint")],
        [EditorValue(text="Unit 1", badge="en", enabled=True)],
        [
            EditorValue(text="A1", enabled=True),
            EditorValue(text="wEvxYRPlmGVQCbZx9GAbn"),
            EditorValue(text="g32qzYNVH1Ez7JTEk3fvLF"),
            EditorValue(text="cWWm02l1c6cucKjIhkFqY4"),
            EditorValue(text="cWWm02l1c6cucKjIhkFqY4"),
            EditorValue(text="1999-12-24", badge="day"),
            EditorValue(text="2023-01-01", badge="day"),
        ],
    ]
