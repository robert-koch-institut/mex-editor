from typing import TYPE_CHECKING

from mex.editor.code_gen.main import ENTITY_NAMES, entity_bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from tests.code_gen.helpers import brackets_balanced, declaration_order_ok

if TYPE_CHECKING:
    from pathlib import Path


def test_all_six_entity_bundles_generate_cleanly(out_dir: Path) -> None:
    bundles = [entity_bundle(n) for n in ENTITY_NAMES]
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
        assert brackets_balanced(text), p
        assert declaration_order_ok(text), p
        assert "z.unknown()" not in text, p
