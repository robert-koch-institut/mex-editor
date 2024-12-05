import pytest

from mex.common.exceptions import MExError
from mex.common.models import AnyExtractedModel
from mex.common.types import APIType
from mex.editor.models import EditorValue
from mex.editor.transform import (
    transform_models_to_preview,
    transform_models_to_title,
    transform_value,
    transform_values,
)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (None, []),
        (
            "foo",
            [EditorValue(text="foo")],
        ),
        (
            ["bar", APIType["REST"]],
            [
                EditorValue(text="bar"),
                EditorValue(text="REST", badge="APIType"),
            ],
        ),
    ],
)
def test_transform_values(values: object, expected: list[EditorValue]) -> None:
    assert transform_values(values) == expected


def test_transform_value_none_error() -> None:
    with pytest.raises(MExError, match="cannot transform null"):
        transform_value(None)


def test_transform_models_to_title_empty() -> None:
    assert transform_models_to_title([]) == []


def test_transform_models_to_title(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_titles = [transform_models_to_title([d]) for d in dummy_data]
    assert dummy_titles == [
        [
            # mex primary source has no title, renders identifier instead
            EditorValue(
                text="sMgFvmdtJyegb9vkebq04",
                href="/item/sMgFvmdtJyegb9vkebq04",
            )
        ],
        [
            # ps-2 primary source has no title either
            EditorValue(
                text="d0MGZryflsy7PbsBF3ZGXO",
                href="/item/d0MGZryflsy7PbsBF3ZGXO",
            )
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
            EditorValue(
                text="Aktivität 1",
                badge="de",
            )
        ],
    ]


def test_transform_models_to_preview_empty() -> None:
    assert transform_models_to_preview([]) == []


def test_transform_models_to_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [transform_models_to_preview([d]) for d in dummy_data]
    assert dummy_previews == [
        [EditorValue(text="ExtractedPrimarySource")],
        [EditorValue(text="ExtractedPrimarySource")],
        [EditorValue(text="ExtractedContactPoint")],
        [EditorValue(text="ExtractedContactPoint")],
        [EditorValue(text="Unit 1", badge="en", enabled=True)],
        [
            EditorValue(text="A1", enabled=True),
            EditorValue(
                text="wEvxYRPlmGVQCbZx9GAbn", href="/item/wEvxYRPlmGVQCbZx9GAbn"
            ),
            EditorValue(
                text="g32qzYNVH1Ez7JTEk3fvLF", href="/item/g32qzYNVH1Ez7JTEk3fvLF"
            ),
            EditorValue(
                text="cWWm02l1c6cucKjIhkFqY4", href="/item/cWWm02l1c6cucKjIhkFqY4"
            ),
            EditorValue(
                text="cWWm02l1c6cucKjIhkFqY4", href="/item/cWWm02l1c6cucKjIhkFqY4"
            ),
            EditorValue(text="24. Dezember 1999"),
            EditorValue(text="1. Januar 2023"),
        ],
    ]
