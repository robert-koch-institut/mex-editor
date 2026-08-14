"""Generates TS interfaces + Angular Signal Forms validators + (experimental)
Zod schemas for all six mex-common entity types. Run:
`python examples/generate_all_entities.py` from the package root, with
mex-common installed. Output goes to `./generated/`.
"""

from __future__ import annotations

from pathlib import Path

import mex.common.models as m

from mex.editor.frontend import CLIENT

from . import (
    AngularSignalFormValidatorGenerator,
    Bundle,
    TypeScriptInterfaceGenerator,
    ZodSchemaGenerator,
    run_generators,
)

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


def main() -> None:
    bundles = [entity_bundle(n) for n in ENTITY_NAMES]
    written = run_generators(
        bundles,
        CLIENT / "src/app/shared/TESTGEN/",
        # Path(__file__).parent / "generated",
        [
            TypeScriptInterfaceGenerator(),
            AngularSignalFormValidatorGenerator(),
            ZodSchemaGenerator(),
        ],
    )
    print(f"Wrote {len(written)} files to {Path(__file__).parent / 'generated'}")


if __name__ == "__main__":
    main()
