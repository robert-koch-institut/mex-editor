from typing import Any

import pytest

from mex.common.models import (
    AnyExtractedModel,
)
from mex.common.types import Identifier, Link, Text
from mex.editor.transform import (
    render_any_value,
    render_model_preview,
    render_model_title,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, ""),
        ({"foo": 42}, "foo: 42"),
        (["foo", 42, Identifier.generate(seed=42)], "foo, 42, bFQoRhcVH5DHU6"),
        (Text.model_validate("This is proper."), "This is proper."),
        (Link(title="Title", url="https://foo"), "https://foo"),
        ("text-text-text", "text-text-text"),
        ({"foo": {"bar": Identifier.generate(seed=42)}}, "foo: bar: bFQoRhcVH5DHU6"),
    ],
    ids=["None", "dict", "list", "Text", "Link", "string-like", "nested"],
)
def test_render_any_value(value: Any, expected: str) -> None:
    assert render_any_value(value) == expected


def test_render_model_title(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_titles = [render_model_title(d) for d in dummy_data]
    assert dummy_titles == [
        "ExtractedPrimarySource",
        "ExtractedPrimarySource",
        "info@contact-point.one",
        "help@contact-point.two",
        "OU1",
        "Aktivität 1",
    ]


def test_render_model_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [render_model_preview(d) for d in dummy_data]
    assert dummy_previews == [
        "sMgFvmdtJyegb9vkebq04",
        "d0MGZryflsy7PbsBF3ZGXO",
        "gs6yL8KJoXRos9l2ydYFfx",
        "vQHKlAQWWraW9NPoB5Ewq",
        "gIyDlXYbq0JwItPRU0NcFN",
        "value: A1 \u2010 cWWm02l1c6cucKjIhkFqY4 \u2010 1999-12-24 \u2010 2023-01-01",
    ]
