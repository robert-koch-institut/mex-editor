"""Written by Claude (Anthropic).

Generates Zod schemas (validation + types) for all six mex-common entity
types. Run: `python examples/generate_all_entities.py` from the package
root, with mex-common installed. Output goes to `./generated/`.
"""
from __future__ import annotations
from pathlib import Path
import click
import mex.common.models as m

from mex.editor.code_gen.bundle import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from mex.editor.frontend import CLIENT

# Every entity family follows the same nine-model shape: Extracted/Merged
# (the real records), Additive/Subtractive/Preventive/Workflow/Preview
# (rule variants), RuleSetRequest/RuleSetResponse.
ENTITY_NAMES = ["Resource", "Activity", "Person", "ContactPoint", "OrganizationalUnit", "Organization"]
DEFAULT_OUTPUT_PATH = CLIENT / "src/app/shared/models/generated"


def entity_bundle(name: str) -> Bundle:
    """Builds the Bundle for one mex-common entity family."""
    class_names = [
        f"Preventive{name}", f"Workflow{name}", f"{name}RuleSetRequest", f"{name}RuleSetResponse",
        f"Merged{name}", f"Extracted{name}", f"Additive{name}", f"Subtractive{name}", f"Preview{name}",
    ]
    return Bundle(name=name, models=[getattr(m, cn) for cn in class_names])


@click.command()
@click.option(
    "--output",
    type=click.Path(dir_okay=True, file_okay=False, resolve_path=True, path_type=Path),
    required=False,
    default=DEFAULT_OUTPUT_PATH,
    help="Path to the target output dir (optional).",
)
def main(output: Path = DEFAULT_OUTPUT_PATH) -> None:
    bundles = [entity_bundle(n) for n in ENTITY_NAMES]
    written = generate_zod_schemas(bundles, output)
    print(f"Wrote {len(written)} files to {output}")


if __name__ == "__main__":
    main()
