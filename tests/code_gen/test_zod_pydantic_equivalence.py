"""Equivalence tests -- pure Python, no Node/JS involved.

Runs the real `generate_zod_schemas()` against synthetic pydantic models,
then checks the generated `.ts` *text* against what `pytypes.fields_of()`
independently resolved from the same pydantic models -- pattern, bounds,
and the `.nullable()`/`.nullish()`/`.optional()` wrapping. This proves the
generator's output structurally matches its own stated source of truth
(the pydantic model), without needing to execute the generated TypeScript.

Separately, a second block of tests exercises pydantic's *own* validation
behavior on hand-built payloads (valid data, and one violation per
constraint kind) -- useful on its own as a sanity check that the
constraints declared on `sample_models.py` actually do what they claim.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import BaseModel, ValidationError

from mex.editor.code_gen.bundle import Bundle
from mex.editor.code_gen.pytypes import FieldSpec, fields_of
from mex.editor.code_gen.zod_generator import generate_zod_schemas

from .sample_models import (
    ExtractedOrganization,
    ExtractedPerson,
    MergedOrganization,
    MergedPerson,
)

if TYPE_CHECKING:
    from collections.abc import Generator

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "generated_ts"


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
    (via pytypes.fields_of -- not from reading zod_generator.py's code),
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
# Structural checks: generated Zod text vs. pydantic's own field metadata
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
    assert expr.startswith("z.number()")
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


def test_entity_type_is_a_bare_literal_with_no_wrapper(
    generated_sources: dict[str, str],
) -> None:
    expr = field_expr(
        generated_sources["organization.ts"],
        "ExtractedOrganizationSchema",
        "entityType",
    )
    assert expr == 'z.literal("ExtractedOrganization")'


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
# pydantic's own validation behavior (pure Python, no generated code
# involved at all -- sanity-checks that sample_models.py's constraints do
# what they claim).
# ---------------------------------------------------------------------------


def pydantic_ok(model: type[BaseModel], payload: dict[str, Any]) -> bool:
    try:
        model.model_validate(payload)
    except ValidationError:
        return False
    return True


VALID_ORG = {
    "name": "RKI",
    "identifier": "abcDEF1234567890",
    "entityType": "ExtractedOrganization",
    "email": "a@b.com",
    "employeeCount": 5,
    "tags": ["research"],
    "status": "active",
    "address": {"street": "Musterstr. 1", "zipCode": "12345"},
    "website": None,
}


@pytest.mark.parametrize(
    ("description", "payload", "expected_valid"),
    [
        ("valid payload", VALID_ORG, True),
        (
            "missing required 'name'",
            {k: v for k, v in VALID_ORG.items() if k != "name"},
            False,
        ),
        ("name too long (>100 chars)", {**VALID_ORG, "name": "x" * 101}, False),
        (
            "identifier fails pattern (too short)",
            {**VALID_ORG, "identifier": "short"},
            False,
        ),
        ("employeeCount negative", {**VALID_ORG, "employeeCount": -1}, False),
        ("employeeCount over max", {**VALID_ORG, "employeeCount": 100_001}, False),
        ("malformed email", {**VALID_ORG, "email": "not-an-email"}, False),
        ("tags empty (violates min_length=1)", {**VALID_ORG, "tags": []}, False),
        (
            "tags too many (violates max_length=5)",
            {**VALID_ORG, "tags": list("abcdef")},
            False,
        ),
        ("invalid status enum value", {**VALID_ORG, "status": "bogus"}, False),
        (
            "nested address missing 'street'",
            {**VALID_ORG, "address": {"zipCode": "12345"}},
            False,
        ),
        (
            "nested address zipCode fails pattern",
            {**VALID_ORG, "address": {"street": "S", "zipCode": "abc"}},
            False,
        ),
        ("website explicit null is valid", {**VALID_ORG, "website": None}, True),
        (
            "website present is valid",
            {**VALID_ORG, "website": "https://example.org"},
            True,
        ),
        (
            "website key omitted entirely is valid",
            {k: v for k, v in VALID_ORG.items() if k != "website"},
            True,
        ),
    ],
)
def test_extracted_organization_validation(
    description: str,
    payload: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
) -> None:
    assert pydantic_ok(ExtractedOrganization, payload) is expected_valid, description


VALID_PERSON = {
    "givenName": "Jane",
    "familyName": "Doe",
    "entityType": "ExtractedPerson",
    "identifier": "abcDEF1234567890",
    "status": "active",
    "birthDate": "2024-01-15",
}


@pytest.mark.parametrize(
    ("description", "payload", "expected_valid"),
    [
        ("valid, full YearMonthDay birthDate", VALID_PERSON, True),
        (
            "valid, YearMonth-only birthDate",
            {**VALID_PERSON, "birthDate": "2024-01"},
            True,
        ),
        ("valid, Year-only birthDate", {**VALID_PERSON, "birthDate": "2024"}, True),
        (
            "birthDate explicit null is valid (nullable, required key)",
            {**VALID_PERSON, "birthDate": None},
            True,
        ),
        (
            "birthDate malformed string matches none of the 3 patterns",
            {**VALID_PERSON, "birthDate": "not-a-date"},
            False,
        ),
        (
            "birthDate key OMITTED is invalid (required even though nullable)",
            {k: v for k, v in VALID_PERSON.items() if k != "birthDate"},
            False,
        ),
        ("identifier fails pattern", {**VALID_PERSON, "identifier": "!!!"}, False),
    ],
)
def test_extracted_person_validation(
    description: str,
    payload: dict[str, Any],
    expected_valid: bool,  # noqa: FBT001
) -> None:
    assert pydantic_ok(ExtractedPerson, payload) is expected_valid, description


def test_merged_person_entity_type_literal_mismatch_is_rejected() -> None:
    valid = {
        "givenName": "Jane",
        "familyName": "Doe",
        "entityType": "MergedPerson",
        "identifier": "abcDEF1234567890",
        "status": "active",
    }
    assert pydantic_ok(MergedPerson, valid) is True
    assert (
        pydantic_ok(MergedPerson, {**valid, "entityType": "ExtractedPerson"}) is False
    )


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
    org = ExtractedOrganization.model_validate(VALID_ORG)
    dumped_with_null = org.model_dump(mode="json", by_alias=True)
    assert dumped_with_null["website"] is None

    org_no_website = ExtractedOrganization.model_validate(
        {k: v for k, v in VALID_ORG.items() if k != "website"}
    )
    dumped_omitted = org_no_website.model_dump(
        mode="json", by_alias=True, exclude_unset=True
    )
    assert "website" not in dumped_omitted
