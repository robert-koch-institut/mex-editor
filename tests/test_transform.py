import pytest

from mex.common.exceptions import MExError
from mex.common.models import AnyExtractedModel
from mex.common.types import APIType
from mex.editor.models import FixedValue
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
            [
                FixedValue(
                    text="foo",
                    badge=None,
                    href=None,
                    tooltip=None,
                    external=False,
                )
            ],
        ),
        (
            ["bar", APIType["REST"]],
            [
                FixedValue(
                    text="bar",
                    badge=None,
                    href=None,
                    tooltip=None,
                    external=False,
                ),
                FixedValue(
                    text="REST",
                    badge="APIType",
                    href=None,
                    tooltip=None,
                    external=False,
                ),
            ],
        ),
    ],
)
def test_transform_values(values: object, expected: list[FixedValue]) -> None:
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
            FixedValue(
                text="sMgFvmdtJyegb9vkebq04",
                badge=None,
                href="/item/sMgFvmdtJyegb9vkebq04",
                tooltip=None,
                external=False,
            )
        ],
        [
            # ps-2 primary source has no title either
            FixedValue(
                text="d0MGZryflsy7PbsBF3ZGXO",
                badge=None,
                href="/item/d0MGZryflsy7PbsBF3ZGXO",
                tooltip=None,
                external=False,
            )
        ],
        [
            # contact-point renders email as text
            FixedValue(
                text="info@contact-point.one",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            # contact-point renders email as text
            FixedValue(
                text="help@contact-point.two",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            # unit renders shortName as text (no language badge)
            FixedValue(
                text="OU1",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            # activity renders title as text (with language badge)
            FixedValue(
                text="Aktivität 1",
                badge="de",
                href=None,
                tooltip=None,
                external=False,
            )
        ],
    ]


def test_transform_models_to_preview_empty() -> None:
    assert transform_models_to_preview([]) == []


def test_transform_models_to_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [transform_models_to_preview([d]) for d in dummy_data]
    assert dummy_previews == [
        [
            FixedValue(
                text="ExtractedPrimarySource",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            FixedValue(
                text="ExtractedPrimarySource",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            FixedValue(
                text="ExtractedContactPoint",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            FixedValue(
                text="ExtractedContactPoint",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            FixedValue(
                text="Unit 1",
                badge="en",
                href=None,
                tooltip=None,
                external=False,
            )
        ],
        [
            FixedValue(
                text="A1",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="wEvxYRPlmGVQCbZx9GAbn",
                badge=None,
                href="/item/wEvxYRPlmGVQCbZx9GAbn",
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="g32qzYNVH1Ez7JTEk3fvLF",
                badge=None,
                href="/item/g32qzYNVH1Ez7JTEk3fvLF",
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="cWWm02l1c6cucKjIhkFqY4",
                badge=None,
                href="/item/cWWm02l1c6cucKjIhkFqY4",
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="cWWm02l1c6cucKjIhkFqY4",
                badge=None,
                href="/item/cWWm02l1c6cucKjIhkFqY4",
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="24. Dezember 1999",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            ),
            FixedValue(
                text="1. Januar 2023",
                badge=None,
                href=None,
                tooltip=None,
                external=False,
            ),
        ],
    ]
