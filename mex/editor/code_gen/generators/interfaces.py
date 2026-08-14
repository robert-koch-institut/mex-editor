"""AI-generated codegen module (Claude). Compact by design.

Writes model/shared{SUFFIX} + model/{Bundle}{SUFFIX} TypeScript interfaces.
"""

from __future__ import annotations
from pathlib import Path
from ..bundle import Bundle
from ..schema_collect import EnumDef, ModelDef, SchemaIndex, referenced_def_names
from ..ts_types import render_def_interface
from ..ts_writer import TSFile
from .base import Generator, import_specifier, write_file


def _direct_refs(entry: ModelDef | EnumDef) -> set[str]:
    if isinstance(entry, EnumDef):
        return set()
    refs = {r for spec in entry.fields for r in referenced_def_names(spec.node)}
    if entry.extends:
        refs.add(entry.extends)
    return refs


class TypeScriptInterfaceGenerator(Generator):
    name = "typescript-interfaces"

    def generate(
        self, index: SchemaIndex, bundles: list[Bundle], output_dir: Path
    ) -> list[Path]:
        shared = index.shared_defs()
        body = "".join(render_def_interface(n, index.defs[n]) for n in sorted(shared))
        written = [
            write_file(
                output_dir, ("models", "shared"), TSFile(body_parts=[body]).render()
            )
        ]

        for bundle in bundles:
            owned = sorted(
                n for n in index.defs if index.owning_bundle(n) == bundle.name
            )
            roots = index.roots[bundle.name]
            owned.sort(key=lambda n: (n not in roots, n))
            needed = {r for n in owned for r in _direct_refs(index.defs[n]) & shared}
            imports = []
            if needed:
                spec = import_specifier(("models", bundle.name), ("models", "shared"))
                imports.append(
                    f"import type {{ {', '.join(sorted(needed))} }} from \"{spec}\";"
                )
            body = "".join(render_def_interface(n, index.defs[n]) for n in owned)
            written.append(
                write_file(
                    output_dir,
                    ("models", bundle.name),
                    TSFile(imports, body_parts=[body]).render(),
                )
            )

        return written
