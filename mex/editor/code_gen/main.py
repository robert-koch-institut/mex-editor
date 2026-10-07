from pathlib import Path
from typing import TYPE_CHECKING

import click

from mex.common.models import (
    ADDITIVE_MODEL_CLASSES_BY_NAME,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MERGED_MODEL_CLASSES_BY_NAME,
    PREVENTIVE_MODEL_CLASSES_BY_NAME,
    PREVIEW_MODEL_CLASSES_BY_NAME,
    RULE_SET_REQUEST_CLASSES_BY_NAME,
    RULE_SET_RESPONSE_CLASSES_BY_NAME,
    SUBTRACTIVE_MODEL_CLASSES_BY_NAME,
    WORKFLOW_MODEL_CLASSES_BY_NAME,
)
from mex.editor.code_gen.models import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas
from mex.editor.frontend import CLIENT, exec_npx

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pydantic import BaseModel

# Every entity family follows the same nine-model shape: Extracted/Merged
# (the real records), Additive/Subtractive/Preventive/Workflow/Preview
# (rule variants), RuleSetRequest/RuleSetResponse.
ENTITY_NAMES = [
    "Resource",
    "Activity",
    "Person",
    "ContactPoint",
    "OrganizationalUnit",
    "Organization",
]
DEFAULT_OUTPUT_PATH = CLIENT / "src/app/shared/models/generated"


# Each family's nine models, looked up through mex-common's own registries
# rather than by rebuilding its naming convention here: a family mex-common
# stops shipping then raises KeyError against a real registry, instead of
# AttributeError from a name this module guessed.
_REGISTRIES: list[tuple[Mapping[str, type[BaseModel]], str]] = [
    (PREVENTIVE_MODEL_CLASSES_BY_NAME, "Preventive{}"),
    (WORKFLOW_MODEL_CLASSES_BY_NAME, "Workflow{}"),
    (RULE_SET_REQUEST_CLASSES_BY_NAME, "{}RuleSetRequest"),
    (RULE_SET_RESPONSE_CLASSES_BY_NAME, "{}RuleSetResponse"),
    (MERGED_MODEL_CLASSES_BY_NAME, "Merged{}"),
    (EXTRACTED_MODEL_CLASSES_BY_NAME, "Extracted{}"),
    (ADDITIVE_MODEL_CLASSES_BY_NAME, "Additive{}"),
    (SUBTRACTIVE_MODEL_CLASSES_BY_NAME, "Subtractive{}"),
    (PREVIEW_MODEL_CLASSES_BY_NAME, "Preview{}"),
]


def entity_bundle(name: str) -> Bundle:
    """Builds the Bundle for one mex-common entity family."""
    return Bundle(
        name=name,
        models=[registry[spelling.format(name)] for registry, spelling in _REGISTRIES],
    )


def format_generated(paths: list[Path]) -> None:
    """Run prettier and then `eslint --fix` over the freshly generated files.

    Only the given files are touched -- never the hand-written sources around
    them. eslint runs last so its fixes end up prettier-formatted too (the
    client's eslint config extends `eslint-plugin-prettier`).
    """
    if not paths:
        return
    files = [p.as_posix() for p in paths]
    exec_npx(["prettier", "--write", *files])
    exec_npx(["eslint", "--fix", *files])


@click.command()
@click.option(
    "--output",
    type=click.Path(dir_okay=True, file_okay=False, resolve_path=True, path_type=Path),
    required=False,
    default=DEFAULT_OUTPUT_PATH,
    help="Path to the target output dir (optional).",
)
def main(output: Path = DEFAULT_OUTPUT_PATH) -> None:
    """Generate Zod schemas (validation + types) for every entity family.

    Writes one file per mex-common entity family into `output`, which defaults
    to the Angular client's `src/app/shared/models/generated/`, then runs the
    client's prettier and eslint over exactly the files it wrote.
    """
    bundles = [entity_bundle(n) for n in ENTITY_NAMES]
    written = generate_zod_schemas(bundles, output)
    click.echo(f"Wrote {len(written)} files to {output}")
    format_generated(written)
