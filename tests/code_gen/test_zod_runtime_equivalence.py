import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from mex.editor.code_gen.models import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from mex.editor.frontend import CLIENT, CLIENT_NODE_MODULES, exec_npx
from tests.code_gen.sample_models import (
    ExtractedOrganization,
    ExtractedPerson,
    MergedOrganization,
    MergedPerson,
)

ROOT = Path(__file__).parent
CASES = ROOT / "equivalence_cases.json"
SPEC = ROOT / "runtime_equivalence.spec.ts"

VITEST_CONFIG = """\
import { defineConfig } from "vitest/config";

export default defineConfig({ test: { include: ["*.spec.ts"] } });
"""


@pytest.mark.integration
def test_generated_zod_agrees_with_pydantic_at_runtime() -> None:
    """Execute the emitted Zod against the same corpus pydantic is fed.

    The structural tests in `test_zod_pydantic_equivalence.py` compare the
    generated `.ts` *text* against the generator's own intermediate
    representation, which cannot catch a systematic mistranslation -- a rule
    that is consistently wrong is consistently asserted. This runs the real
    thing: same `equivalence_cases.json`, byte-identical payloads, so any
    disagreement between the two validators fails the build.
    """
    if not CLIENT_NODE_MODULES.is_dir():
        pytest.skip("frontend not installed -- run `uv run install-frontend` first")

    # Inside CLIENT so node resolves zod/vitest from the client's node_modules
    # -- pytest's tmp_path lives outside the client, where that upward lookup
    # would fail. `tmp` prefix so the repo's existing `tmp*/` ignore rule
    # covers it; `tsconfig.app.json` only includes `src/**`, so it stays
    # invisible to `ng build`/`ng lint` either way.
    fixture_dir = Path(tempfile.mkdtemp(prefix="tmp_zod_equivalence_", dir=CLIENT))
    try:
        generate_zod_schemas(
            [
                Bundle(
                    name="Organization",
                    models=[ExtractedOrganization, MergedOrganization],
                ),
                Bundle(name="Person", models=[ExtractedPerson, MergedPerson]),
            ],
            fixture_dir,
        )
        shutil.copyfile(CASES, fixture_dir / "cases.json")
        shutil.copyfile(SPEC, fixture_dir / "runtime_equivalence.spec.ts")
        (fixture_dir / "vitest.config.ts").write_text(VITEST_CONFIG)

        try:
            exec_npx(["vitest", "run", "--root", fixture_dir.as_posix()])
        except subprocess.CalledProcessError as error:
            pytest.fail(f"generated Zod disagrees with pydantic (vitest: {error})")
    finally:
        shutil.rmtree(fixture_dir, ignore_errors=True)
