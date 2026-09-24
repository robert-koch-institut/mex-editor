"""Written by Claude (Anthropic).

Tests against the real mex-common models.

Environment: mex-common==3.0.0 / mex-model==5.0.3 from PyPI. Everything is
resolved from the real Python/pydantic annotations (pytypes.py), not
model_json_schema() -- see pytypes.py docstring for why.

Layout: shared.ts + form-schemas.ts + one {bundle}.ts per bundle, all
flat under the output dir (no subfolders). File names are kebab-case.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

import mex.common.models as m
from mex.common.models import (
    ActivityRuleSetResponse,
    ExtractedActivity,
    ExtractedResource,
    MergedActivity,
    MergedResource,
    ResourceRuleSetResponse,
)
from mex.editor.code_gen.bundle import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas, kebab

if TYPE_CHECKING:
    from collections.abc import Generator

EXT = ".ts"


@pytest.fixture
def bundles() -> list[Bundle]:
    return [
        Bundle(
            name="Activity",
            models=[ExtractedActivity, MergedActivity, ActivityRuleSetResponse],
        ),
        Bundle(
            name="Resource",
            models=[ExtractedResource, MergedResource, ResourceRuleSetResponse],
        ),
    ]


@pytest.fixture
def out_dir() -> Generator[Path, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def bundle_file(out_dir: Path, bundle: str) -> Path:
    return out_dir / f"{kebab(bundle)}{EXT}"


def shared_file(out_dir: Path) -> Path:
    return out_dir / f"shared{EXT}"


def _brackets_balanced(text: str) -> bool:
    return text.count("{") == text.count("}") and text.count("(") == text.count(")")


def _declaration_order_ok(text: str) -> bool:
    """Checks if the declartion order is ok.

    No `const`/`type` is referenced (outside its own declaration line
    or its doc comment) before it's declared -- const isn't hoisted in
    JS, so a forward reference throws at runtime, not just a lint issue.
    """
    lines = text.splitlines()
    declared_at: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = re.match(r"export (?:const|type) (\w+)", line)
        if m:
            declared_at[m.group(1)] = i
    code_lines = [
        (i, re.sub(r'"(?:[^"\\]|\\.)*"', '""', line))
        for i, line in enumerate(lines)
        if not re.match(r"\s*(/\*\*|\*|\*/)", line)
    ]
    for name, at in declared_at.items():
        for i, line in code_lines:
            if i != at and re.search(rf"\b{re.escape(name)}\b", line) and i < at:
                return False
    return True


# ---------------------------------------------------------------------------


def test_output_is_flat_one_file_per_bundle(
    bundles: list[Bundle], out_dir: Path
) -> None:
    written = generate_zod_schemas(bundles, out_dir)
    rel = {p.relative_to(out_dir).as_posix() for p in written}
    assert rel == {
        f"shared{EXT}",
        f"activity{EXT}",
        f"resource{EXT}",
    }
    assert all("/" not in r for r in rel)  # no subfolders


def test_no_generated_infix_in_filenames(bundles: list[Bundle], out_dir: Path) -> None:
    written = generate_zod_schemas(bundles, out_dir)
    assert all(".generated" not in p.name for p in written)
    assert all(p.suffix == ".ts" for p in written)


def test_bundle_file_contains_both_entities_and_support_defs(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    assert "export const ExtractedActivitySchema" in text
    assert "export const MergedActivitySchema" in text
    assert "export const ActivityRuleSetResponseSchema" in text
    assert "export const BaseActivitySchema" in text  # factored-out base, same file now
    assert (
        "export const AdditiveActivitySchema" in text
    )  # rule sub-model, same file now


def test_declaration_order_is_always_dependency_first(
    bundles: list[Bundle], out_dir: Path
) -> None:
    written = generate_zod_schemas(bundles, out_dir)
    for p in written:
        assert _declaration_order_ok(p.read_text()), (
            f"{p} references a const before it's declared"
        )


def test_every_generated_file_has_balanced_brackets(
    bundles: list[Bundle], out_dir: Path
) -> None:
    for p in generate_zod_schemas(bundles, out_dir):
        assert _brackets_balanced(p.read_text()), p


def test_every_file_disables_naming_convention_lint(
    bundles: list[Bundle], out_dir: Path
) -> None:
    for p in generate_zod_schemas(bundles, out_dir):
        assert p.read_text().startswith(
            "/* eslint-disable @typescript-eslint/naming-convention */\n"
        )


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


def test_referenced_model_field_matches_pydantic_strictly(
    bundles: list[Bundle], out_dir: Path
) -> None:
    # No string-or-object union anymore -- a field referencing another
    # model requires that model's schema, exactly like pydantic does.
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    assert "additive: AdditiveActivitySchema.optional()," in text
    assert "z.union([z.string(), AdditiveActivitySchema])" not in text


def test_text_and_link_schemas_are_plain_objects_not_unions(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    shared = shared_file(out_dir).read_text()
    assert "export const TextSchema = z.object({" in shared
    assert "export const LinkSchema = z.object({" in shared
    assert "TextSchema = z.union(" not in shared
    assert "LinkSchema = z.union(" not in shared


def test_fields_referencing_text_or_link_use_the_plain_schema(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    assert "z.array(TextSchema)" in text
    assert "z.array(LinkSchema)" in text
    assert "z.union([z.string(), TextSchema])" not in text
    assert "z.union([z.string(), LinkSchema])" not in text


def test_relative_imports_always_start_with_dot(
    bundles: list[Bundle], out_dir: Path
) -> None:
    known_packages = {"zod", "@angular/forms/signals"}
    for p in generate_zod_schemas(bundles, out_dir):
        for line in p.read_text().splitlines():
            m = re.search(r'from "([^"]+)"', line)
            if m and m.group(1) not in known_packages:
                assert m.group(1).startswith(("./", "../")), (
                    f"{p}: {line!r} is not a valid relative import"
                )


def test_type_discriminator_is_a_fixed_literal_never_optional(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = bundle_file(out_dir, "Activity").read_text()
    assert '$type: z.literal("ExtractedActivity"),' in text
    assert '$type: z.literal("ExtractedActivity").optional()' not in text


def test_pattern_constants_are_deduplicated_and_untyped(
    bundles: list[Bundle], out_dir: Path
) -> None:
    generate_zod_schemas(bundles, out_dir)
    text = shared_file(out_dir).read_text()
    assert text.count("identifierPattern =") == 1
    assert re.search(r"export const \w+ = \"", text)
    assert not re.search(r"export const \w+: string = ", text)


def test_nullable_optional_field_uses_nullish(out_dir: Path) -> None:
    # Regression: pydantic dumps an unset Optional[X] field as explicit
    # JSON null, not a missing key -- .optional() alone rejects that.

    bundle = Bundle(name="Resource", models=[m.ExtractedResource])
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


def test_all_six_entity_bundles_generate_cleanly(out_dir: Path) -> None:
    def entity_bundle(name: str) -> Bundle:
        class_names = [
            f"Preventive{name}",
            f"Workflow{name}",
            f"{name}RuleSetRequest",
            f"{name}RuleSetResponse",
            f"Merged{name}",
            f"Extracted{name}",
            f"Additive{name}",
            f"Subtractive{name}",
            f"Preview{name}",
        ]
        return Bundle(name=name, models=[getattr(m, cn) for cn in class_names])

    bundles = [
        entity_bundle(n)
        for n in [
            "Resource",
            "Activity",
            "Person",
            "ContactPoint",
            "OrganizationalUnit",
            "Organization",
        ]
    ]
    written = generate_zod_schemas(bundles, out_dir)
    rel = {p.relative_to(out_dir).as_posix() for p in written}
    assert rel == {
        "shared.ts",
        "resource.ts",
        "activity.ts",
        "person.ts",
        "contact-point.ts",
        "organizational-unit.ts",
        "organization.ts",
    }
    for p in written:
        text = p.read_text()
        assert _brackets_balanced(text), p
        assert _declaration_order_ok(text), p
        assert "z.unknown()" not in text, p
