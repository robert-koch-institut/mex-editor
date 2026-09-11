import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, Field

from mex.editor.code_gen.main import ENTITY_NAMES, entity_bundle
from mex.editor.code_gen.patterns import PatternRegistry, _name, js_incompatibility
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from tests.code_gen.helpers import generate, shared_file

if TYPE_CHECKING:
    from mex.editor.code_gen.models import Bundle


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        (r"(?P<year>\d{4})", "named group"),
        (r"(?P<y>\d)-(?P=y)", "named group"),
        (r"(?#a comment)\d+", "inline comment"),
        (r"(?i)abc", "inline flag group"),
        (r"(?>\d+)x", "atomic group"),
        (r"\Aabc", "`\\A` anchor"),
        (r"abc\Z", "`\\Z` anchor"),
        (r"abc\z", "`\\z` anchor"),
    ],
)
def test_python_only_regex_constructs_are_detected(pattern: str, expected: str) -> None:
    problem = js_incompatibility(pattern)
    assert problem is not None, pattern
    assert expected in problem


@pytest.mark.parametrize(
    "pattern",
    [
        r"^[a-zA-Z0-9]{14,22}$",
        r"^\d{4}-\d{2}-\d{2}$",
        r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$",
        r"^(?:0[1-9]|1[0-2])$",
        r"(?<=x)y",  # lookbehind: fine in modern JavaScript
        r"a\\Ab",  # an escaped backslash, not the \A anchor
        r"a\\Zb",
    ],
)
def test_javascript_compatible_patterns_are_left_alone(pattern: str) -> None:
    assert js_incompatibility(pattern) is None
    # Sanity: these really are patterns Python itself accepts.
    re.compile(pattern)


def test_registering_a_python_only_pattern_raises_with_context() -> None:
    registry = PatternRegistry()
    with pytest.raises(ValueError, match="cannot be compiled by JavaScript") as excinfo:
        registry.name_for(r"(?P<year>\d{4})", "Year", "birthDate")
    assert "Year.birthDate" in str(excinfo.value)


def test_a_python_only_pattern_fails_the_whole_generation() -> None:
    # A named group is the realistic case: pydantic's own regex engine accepts
    # `(?P<...>)` happily, so nothing upstream of the generator objects to it.
    class HasBadPattern(BaseModel):
        code: str = Field(pattern=r"^(?P<year>\d{4})$")

    with pytest.raises(ValueError, match="cannot be compiled by JavaScript"):
        generate([HasBadPattern])


def test_every_pattern_in_the_real_output_is_javascript_compatible() -> None:

    output_dir = Path(tempfile.mkdtemp(prefix="guardrails_real_"))
    written = generate_zod_schemas([entity_bundle(n) for n in ENTITY_NAMES], output_dir)
    shared = next(p for p in written if p.name == "shared.ts").read_text()
    patterns = re.findall(r'^export const \w+Pattern = "(.*)";$', shared, re.MULTILINE)
    assert patterns, "no patterns found in shared.ts"
    for pattern in patterns:
        assert js_incompatibility(pattern) is None, pattern


def test_a_field_name_starting_with_a_digit_gets_a_usable_pattern_name() -> None:
    # `_2fa` used to yield `2faPattern`, which is not a TS identifier.
    assert not _name("_2fa")[0].isdigit()
    assert _name("_2fa") == "value2faPattern"
    assert _name("email") == "emailPattern"


def test_pattern_constants_are_deduplicated_and_untyped(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = shared_file(out_dir).read_text()
    assert text.count("identifierPattern =") == 1
    assert re.search(r"export const \w+ = \"", text)
    assert not re.search(r"export const \w+: string = ", text)
