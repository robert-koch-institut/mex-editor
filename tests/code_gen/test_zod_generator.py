import re
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from mex.editor.code_gen.zod_generator import HEADER, _topo_order, generate_zod_schemas
from tests.code_gen.helpers import (
    EXT,
    brackets_balanced,
    bundle_file,
    declaration_order_ok,
    generate,
)
from tests.code_gen.sample_models import HasOpaqueField, UnionWithFieldConstraint

if TYPE_CHECKING:
    from pathlib import Path

    from mex.editor.code_gen.models import Bundle


def test_topo_order_still_orders_a_plain_dependency_chain() -> None:
    order = _topo_order(["A", "B", "C"], {"A": {"B"}, "B": {"C"}})
    assert order == ["C", "B", "A"]


def test_topo_order_ignores_dependencies_outside_the_file() -> None:
    # Refs to defs living in another file are imported, not declared here.
    assert _topo_order(["A"], {"A": {"Elsewhere"}}) == ["A"]


def test_topo_order_raises_on_a_two_step_cycle() -> None:
    with pytest.raises(ValueError, match="Cyclic schema reference") as excinfo:
        _topo_order(["A", "B"], {"A": {"B"}, "B": {"A"}})
    assert "z.lazy()" in str(excinfo.value)


def test_topo_order_raises_on_a_self_reference() -> None:
    with pytest.raises(ValueError, match=r"Cyclic schema reference: A -> A"):
        _topo_order(["A"], {"A": {"A"}})


def test_a_recursive_model_is_refused_instead_of_generated() -> None:
    class Tree(BaseModel):
        label: str
        child: Tree | None = None

    with pytest.raises(ValueError, match="Cyclic schema reference"):
        generate([Tree])


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
        assert declaration_order_ok(p.read_text()), (
            f"{p} references a const before it's declared"
        )


def test_every_generated_file_has_balanced_brackets(
    bundles: list[Bundle], out_dir: Path
) -> None:
    for p in generate_zod_schemas(bundles, out_dir):
        assert brackets_balanced(p.read_text()), p


def test_every_file_disables_naming_convention_lint(
    bundles: list[Bundle], out_dir: Path
) -> None:
    for p in generate_zod_schemas(bundles, out_dir):
        assert p.read_text().startswith(
            "/* eslint-disable @typescript-eslint/naming-convention */\n"
        )


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


def test_the_generated_header_names_the_command_that_regenerates_it() -> None:
    assert "generate-ts-models" in HEADER


def test_the_generated_files_carry_that_header() -> None:
    assert HEADER in generate([UnionWithFieldConstraint])["thing.ts"]


def test_an_unresolvable_field_is_logged_as_a_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("WARNING"):
        generate([HasOpaqueField])
    assert any("HasOpaqueField.thing" in record.message for record in caplog.records)
