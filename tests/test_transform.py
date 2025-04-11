import pytest

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
                EditorValue(text="APIType", badge="REST"),
                EditorValue(text="hi there", badge="EN"),
                EditorValue(
                    text="homepage", badge="EN", href="http://mex", external=True
                ),
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            True,
            [
                EditorValue(
                    href="/item/cWWm02l1c6cucKjIhkFqY4",
                    identifier="cWWm02l1c6cucKjIhkFqY4",
                )
            ],
        ),
        (
            Identifier("cWWm02l1c6cucKjIhkFqY4"),
            False,
            [
                EditorValue(
                    identifier="cWWm02l1c6cucKjIhkFqY4",
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
    with pytest.raises(
        NotImplementedError, match="cannot transform NoneType to editor value"
    ):
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
            EditorValue(text="Primary Source One", badge="EN")
        ],
        [
            # ps-2 primary source renders title as text
            EditorValue(text="Primary Source Two", badge="EN")
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
            EditorValue(text="Aktivität 1", badge="DE")
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
        [EditorValue(text="Unit 1", badge="EN", enabled=True)],
        [
            EditorValue(text="A1", enabled=True),
            EditorValue(
                identifier="wEvxYRPlmGVQCbZx9GAbn",
            ),
            EditorValue(
                identifier="g32qzYNVH1Ez7JTEk3fvLF",
            ),
            EditorValue(
                identifier="cWWm02l1c6cucKjIhkFqY4",
            ),
            EditorValue(
                identifier="cWWm02l1c6cucKjIhkFqY4",
            ),
            EditorValue(
                text="1999-12-24",
                badge="day",
            ),
            EditorValue(
                text="2023-01-01",
                badge="day",
            ),
        ],
    ]
