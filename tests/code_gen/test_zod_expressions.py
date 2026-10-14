from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Literal

import pytest
from pydantic import BaseModel, Field

from mex.common.models import ExtractedActivity, ExtractedResource
from mex.editor.code_gen.models import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from tests.code_gen.helpers import bundle_file, generate, shared_file
from tests.code_gen.sample_models import HasOpaqueField, UnionWithFieldConstraint

if TYPE_CHECKING:
    from pathlib import Path


def test_enum_members_are_json_escaped() -> None:
    class Quoted(Enum):
        SAID = 'he said "hi"'
        SLASH = "back\\slash"

    class HasQuoted(BaseModel):
        q: Quoted

    source = generate([HasQuoted])["thing.ts"]
    [line] = [x for x in source.splitlines() if x.startswith("export const Quoted")]
    assert (
        line
        == r'export const QuotedSchema = z.enum(["he said \"hi\"", "back\\slash"]);'
    )


def test_a_non_string_enum_is_not_emitted_as_a_string_enum() -> None:
    class Priority(IntEnum):
        LOW = 1
        HIGH = 2

    class HasPriority(BaseModel):
        p: Priority

    source = generate([HasPriority])["thing.ts"]
    [line] = [x for x in source.splitlines() if x.startswith("export const Priority")]
    # pydantic accepts the number 1 here, so z.enum(["1", "2"]) would be wrong.
    assert line == "export const PrioritySchema = z.literal([1, 2]);"


def test_a_literal_of_enum_members_emits_their_values() -> None:
    class Colour(Enum):
        RED = "red"

    class HasLiteralEnum(BaseModel):
        c: Literal[Colour.RED]

    source = generate([HasLiteralEnum])["thing.ts"]
    [line] = [line for line in source.splitlines() if line.strip().startswith("c:")]
    assert line.strip() == 'c: z.literal("red"),'


@pytest.mark.parametrize(
    ("alias", "expected_key"),
    [
        ("content-type", '"content-type"'),
        ("@context", '"@context"'),
        ("has space", '"has space"'),
        ("2fast", '"2fast"'),
        ("$type", "$type"),  # `$` is a legal identifier character
        ("class", "class"),  # reserved words are legal property names
        ("entityType", "entityType"),
    ],
)
def test_object_keys_are_quoted_only_when_they_have_to_be(
    alias: str, expected_key: str
) -> None:
    class Aliased(BaseModel):
        value: str = Field(alias=alias)

    source = generate([Aliased])["thing.ts"]
    [line] = [line for line in source.splitlines() if "z.string()" in line]
    assert line.strip() == f"{expected_key}: z.string(),"


def test_the_generated_union_carries_the_constraint_on_both_branches() -> None:
    source = generate([UnionWithFieldConstraint])["thing.ts"]
    [line] = [line for line in source.splitlines() if line.strip().startswith("code:")]
    assert line.count(".min(4)") == 2


def test_an_unresolvable_field_still_falls_back_to_z_unknown() -> None:
    assert "thing: z.unknown()" in generate([HasOpaqueField])["thing.ts"]


def test_an_unresolvable_field_is_marked_in_the_generated_source() -> None:
    source = generate([HasOpaqueField])["thing.ts"]
    assert "// UNRESOLVED -- accepts anything:" in source
    # The marker sits on its own line, directly above the field it explains,
    # so the one-field-per-line shape of the output is preserved.
    lines = source.splitlines()
    marker = next(i for i, line in enumerate(lines) if "UNRESOLVED" in line)
    assert lines[marker + 1].strip().startswith("thing:")


def test_the_unresolved_marker_explains_why_and_stays_on_one_line() -> None:
    source = generate([HasOpaqueField])["thing.ts"]
    [marker] = [line for line in source.splitlines() if "UNRESOLVED" in line]
    assert "Opaque" in marker
    assert "PydanticSchemaGenerationError" in marker


def test_resolvable_models_get_no_unresolved_marker() -> None:
    class Plain(BaseModel):
        name: str

    assert "UNRESOLVED" not in generate([Plain])["thing.ts"]


def test_referenced_model_field_matches_pydantic_strictly(
    bundles: list[Bundle], out_dir: Path
) -> None:
    # No string-or-object union anywhere -- a field referencing another model
    # requires that model's schema, exactly like pydantic does.
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    shared = shared_file(out_dir).read_text()
    assert "additive: AdditiveActivitySchema.optional()," in text
    assert "z.array(TextSchema)" in text
    assert "z.array(LinkSchema)" in text
    assert "export const TextSchema = z.object({" in shared
    assert "z.union([z.string(), " not in text
    assert "z.union([z.string(), " not in shared


def test_type_discriminator_is_an_optional_literal(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    # mex-common defaults every `$type`, so pydantic accepts a payload without
    # it; the schema has to agree. .default() rather than .optional() so the
    # inferred output type keeps `$type` non-optional and unions still narrow.
    assert not ExtractedActivity.model_fields["entityType"].is_required()
    assert '$type: z.literal("ExtractedActivity").default("ExtractedActivity"),' in text


def test_nullable_optional_field_uses_nullish(out_dir: Path) -> None:
    # Regression: pydantic dumps an unset Optional[X] field as explicit
    # JSON null, not a missing key -- .optional() alone rejects that.

    bundle = Bundle(name="Resource", models=[ExtractedResource])
    generate_zod_schemas([bundle], out_dir)
    text = bundle_file(out_dir, "Resource").read_text()
    assert "accrualPeriodicity: " in text
    line = next(
        l
        for l in text.splitlines()  # noqa: E741
        if l.strip().startswith("accrualPeriodicity:")
    )
    assert ".nullish()" in line or ".nullable()" in line
    assert line.strip().endswith(".optional(),") is False


def test_every_export_has_a_block_style_doc_comment(
    bundles: list[Bundle], out_dir: Path
) -> None:
    for p in generate_zod_schemas(bundles, out_dir):
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            if line.startswith("export "):
                assert lines[i - 1].strip() == "*/", (
                    f"{p}: {line!r} not preceded by a /** */ block comment"
                )
