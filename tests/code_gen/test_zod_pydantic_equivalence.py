import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import BaseModel, ValidationError

from mex.editor.code_gen.models import Bundle, FieldSpec
from mex.editor.code_gen.types import fields_of
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from tests.code_gen.sample_models import (
    ExtractedOrganization,
    ExtractedPerson,
    MergedOrganization,
    MergedPerson,
)

if TYPE_CHECKING:
    from collections.abc import Generator

ROOT = Path(__file__).parent


@pytest.fixture(scope="session")
def generated_sources() -> Generator[dict[str, str], Any]:
    # Writes to a fresh temp dir (not a fixed folder next to this file) and
    # deletes it again once the whole test session finishes, so nothing
    # generated ends up lingering in the repo.
    output_dir = Path(tempfile.mkdtemp(prefix="zod_pydantic_equivalence_"))
    try:
        bundles = [
            Bundle(
                name="Organization", models=[ExtractedOrganization, MergedOrganization]
            ),
            Bundle(name="Person", models=[ExtractedPerson, MergedPerson]),
        ]
        written = generate_zod_schemas(bundles, output_dir)
        yield {p.name: p.read_text() for p in written}
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def field_expr(source: str, schema_name: str, field_name: str) -> str:
    """Field expression helper function.

    Extract the single-line Zod expression generated for one field of
    one schema -- e.g. field_expr(src, "ExtractedOrganizationSchema",
    "email") -> "z.string().email()". Generated code is one field per
    line by construction (see zod_generator.render_zod_schema's `fields`
    list, each appended as `f"  {alias}: {z},"`), so this is a plain
    per-line regex, not a bracket-balancing parser. The schema's own
    `{...}` block is located first so a field name shared with a
    *different* schema in the same file can't be matched by accident.
    """
    block_match = re.search(
        rf"export const {re.escape(schema_name)} = .*?\{{(.*?)\}}\);",
        source,
        re.DOTALL,
    )
    assert block_match, f"schema {schema_name!r} not found in generated source"
    block = block_match.group(1)
    field_match = re.search(
        rf"^\s*{re.escape(field_name)}: (.+),$", block, re.MULTILINE
    )
    assert field_match, f"field {field_name!r} not found in schema {schema_name!r}"
    return field_match.group(1)


def spec_of(model: type, py_name: str) -> FieldSpec:
    [spec] = [f for f in fields_of(model) if f.py_name == py_name]
    return spec


def expected_nullability_suffix(model: type, py_name: str) -> str:
    """Model to null, nullish or optional zod spec.

    Independently derives, from pydantic's own resolved field metadata
    (via types.fields_of -- not from reading zod_generator.py's code),
    what suffix a non-literal field's zod expression should end with.
    """
    spec = spec_of(model, py_name)
    if spec.nullable and not spec.required:
        return ".nullish()"
    if spec.nullable:
        return ".nullable()"
    if not spec.required:
        return ".optional()"
    return ""


# ---------------------------------------------------------------------------
# Structural checks: generated Zod text vs. pydantic's own field metadata.
#
# Proves the output matches its stated source of truth without executing any
# TypeScript. `test_zod_runtime_equivalence.py` is the half that does execute it.
# ---------------------------------------------------------------------------


def test_name_has_min_and_max_length_from_the_pydantic_field(
    generated_sources: dict[str, str],
) -> None:
    # name/identifier were factored into OrganizationBaseSchema (both
    # ExtractedOrganization and MergedOrganization share it) -- that's the
    # point of `extends`, so they don't reappear in the subclass's block.
    expr = field_expr(
        generated_sources["organization.ts"], "OrganizationBaseSchema", "name"
    )
    assert ".min(1)" in expr
    assert ".max(100)" in expr


def test_identifier_uses_the_identifier_pattern_and_correct_nullability(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "OrganizationBaseSchema", "identifier"
    )
    suffix = expected_nullability_suffix(ExtractedOrganization, "identifier")
    assert expr == f"z.string().regex(new RegExp(identifierPattern)){suffix}"


def test_email_uses_the_email_format(generated_sources: dict[str, str]) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "ExtractedOrganizationSchema", "email"
    )
    assert ".string().regex(new RegExp(emailPattern))" in expr


def test_employee_count_has_the_pydantic_bounds(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"],
        "ExtractedOrganizationSchema",
        "employeeCount",
    )
    # z.int(), not z.number(): pydantic rejects 1.5 for an `int` field.
    assert expr.startswith("z.int()")
    assert ".min(0)" in expr
    assert ".max(100000)" in expr


def test_tags_is_an_array_with_the_pydantic_min_and_max(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "ExtractedOrganizationSchema", "tags"
    )
    assert expr.startswith("z.array(z.string())")
    assert ".min(1)" in expr
    assert ".max(5)" in expr


def test_status_references_the_shared_enum_schema(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "ExtractedOrganizationSchema", "status"
    )
    assert expr == "StatusSchema"


def test_address_references_the_nested_object_schema(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "ExtractedOrganizationSchema", "address"
    )
    assert expr == "AddressSchema"


def test_website_wrapping_matches_pydantics_optional_and_nullable_flags(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "ExtractedOrganizationSchema", "website"
    )
    suffix = expected_nullability_suffix(ExtractedOrganization, "website")
    assert (
        suffix == ".nullish()"
    )  # sanity: pydantic really does say optional+nullable here
    assert expr == f"z.string(){suffix}"


def test_entity_type_is_optional_because_pydantic_defaults_it(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"],
        "ExtractedOrganizationSchema",
        "entityType",
    )
    # `entity_type: Literal["X"] = "X"` is NOT required in pydantic, so omitting
    # the key must validate here too. .default() gives that while keeping the
    # inferred output type non-optional, so TypeScript can still narrow on it.
    assert not spec_of(ExtractedOrganization, "entity_type").required
    assert expr == (
        'z.literal("ExtractedOrganization").default("ExtractedOrganization")'
    )


def test_nested_address_zip_code_uses_its_own_pattern(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(generated_sources["organization.ts"], "AddressSchema", "zipCode")
    assert "regex(new RegExp(zipcodePattern))" in expr


def test_merged_organization_extends_the_shared_base(
    generated_sources: dict[str, str],
) -> None:
    source = generated_sources["organization.ts"]
    assert (
        "export const MergedOrganizationSchema = OrganizationBaseSchema.extend({"
        in source
    )


def test_merged_organization_address_wrapping_matches_pydantic(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"], "MergedOrganizationSchema", "address"
    )
    suffix = expected_nullability_suffix(MergedOrganization, "address")
    assert suffix == ".nullish()"
    assert expr == f"AddressSchema{suffix}"


def test_birth_date_is_a_union_of_all_three_temporal_patterns_and_nullable_not_nullish(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["person.ts"], "ExtractedPersonSchema", "birthDate"
    )
    assert "yearMonthDayPattern" in expr
    assert "yearMonthPattern" in expr
    assert "yearPattern" in expr
    suffix = expected_nullability_suffix(ExtractedPerson, "birth_date")
    assert (
        suffix == ".nullable()"
    )  # nullable AND required -> .nullable(), not .nullish()
    assert expr.endswith(suffix)


def test_person_base_is_factored_out_and_shared_by_both_person_models(
    generated_sources: dict[str, str],
) -> None:
    source = generated_sources["person.ts"]
    assert "export const PersonBaseSchema = z.object({" in source
    assert "export const ExtractedPersonSchema = PersonBaseSchema.extend({" in source
    assert "export const MergedPersonSchema = PersonBaseSchema.extend({" in source


def test_status_enum_is_factored_into_shared_ts_and_imported_not_duplicated(
    generated_sources: dict[str, str],
) -> None:
    assert (
        'export const StatusSchema = z.enum(["active", "inactive"]);'
        in generated_sources["shared.ts"]
    )
    assert "export const StatusSchema" not in generated_sources["organization.ts"]
    assert "export const StatusSchema" not in generated_sources["person.ts"]
    assert "import { StatusSchema" in generated_sources["organization.ts"]
    assert "import { StatusSchema" in generated_sources["person.ts"]


# ---------------------------------------------------------------------------
# Behavioural checks: the shared case corpus, run through pydantic.
#
# `equivalence_cases.json` is the single source of truth for these payloads --
# test_zod_runtime_equivalence.py feeds the very same file to the generated
# Zod schemas, so the two validators can be compared case for case.
# ---------------------------------------------------------------------------


MODELS: dict[str, type[BaseModel]] = {
    "ExtractedOrganization": ExtractedOrganization,
    "ExtractedPerson": ExtractedPerson,
    "MergedOrganization": MergedOrganization,
    "MergedPerson": MergedPerson,
}


def load_cases() -> list[tuple[str, type[BaseModel], dict[str, Any], bool]]:
    """Flatten `equivalence_cases.json` into pytest parameters."""
    corpus = json.loads((ROOT / "equivalence_cases.json").read_text())
    return [
        (
            f"{group['model']}: {case['description']}",
            MODELS[group["model"]],
            case["payload"],
            case["valid"],
        )
        for group in corpus
        for case in group["cases"]
    ]


def pydantic_ok(model: type[BaseModel], payload: dict[str, Any]) -> bool:
    try:
        model.model_validate(payload)
    except ValidationError:
        return False
    return True


@pytest.mark.parametrize(
    ("description", "model", "payload", "expected_valid"), load_cases()
)
def test_shared_corpus_against_pydantic(
    description: str,
    model: type[BaseModel],
    payload: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
) -> None:
    assert pydantic_ok(model, payload) is expected_valid, description


def test_pydantics_own_json_dump_of_an_unset_optional_field_is_explicit_null() -> None:
    """Test null and undefined serialization.

    The actual reason `.nullish()` (vs. plain `.nullable()`) exists,
    per zod_generator.py's own comment: pydantic's `model_dump(mode="json")`
    always emits an unset-Optional field as an explicit JSON `null`, not a
    missing key -- while `exclude_unset=True` can still omit it entirely.
    Both shapes need to be *accepted*, which `.nullish()` structurally
    guarantees (it allows both `null` and `undefined`/missing) -- see
    `test_website_wrapping_matches_pydantics_optional_and_nullable_flags`
    above for the structural half of this claim.
    """
    valid_org = next(
        case["payload"]
        for group in json.loads((ROOT / "equivalence_cases.json").read_text())
        if group["model"] == "ExtractedOrganization"
        for case in group["cases"]
        if case["description"] == "valid payload"
    )
    org = ExtractedOrganization.model_validate(valid_org)
    dumped_with_null = org.model_dump(mode="json", by_alias=True)
    assert dumped_with_null["website"] is None

    org_no_website = ExtractedOrganization.model_validate(
        {k: v for k, v in valid_org.items() if k != "website"}
    )
    dumped_omitted = org_no_website.model_dump(
        mode="json", by_alias=True, exclude_unset=True
    )
    assert "website" not in dumped_omitted
