"""AI-generated codegen module (Claude). Compact by design.

EXPERIMENTAL. Writes real Zod schemas: zod/shared{SUFFIX} (patterns +
validators for defs used by >1 bundle), zod/{Bundle}/{EntityModel}{SUFFIX}
per requested root model, zod/{Bundle}/support{SUFFIX} for everything else
that bundle needs -- schema + inferred type together, unlike the
TS-interfaces/Angular-validators pair which keeps those separate.
"""
from __future__ import annotations
import json
from pathlib import Path
from ..bundle import Bundle
from ..patterns import PatternRegistry
from ..schema_collect import SchemaIndex
from ..ts_writer import TSFile
from ..ts_zod import ZodResult, render_zod_schema
from .base import Generator, import_specifier, write_file


def _loc(name: str, index: SchemaIndex, shared: set[str]) -> tuple[str, ...]:
    if name in shared:
        return ("zod", "shared")
    owner = index.owning_bundle(name)
    return ("zod", owner, name) if name in index.roots[owner] else ("zod", owner, "support")


class ZodSchemaGenerator(Generator):
    name = "zod-schemas"

    def generate(self, index: SchemaIndex, bundles: list[Bundle], output_dir: Path) -> list[Path]:
        shared = index.shared_defs()
        patterns = PatternRegistry()
        results = {n: render_zod_schema(n, e, patterns) for n, e in index.defs.items()}
        all_patterns = {p for r in results.values() for p in r.pattern_names}
        written: list[Path] = [            ]

        if shared or all_patterns:
            prelude = ""
            if all_patterns:
                lines = [f"export const {n}: string = {json.dumps(p)};" for p, n in patterns.all_patterns().items() if n in all_patterns]
                prelude = "// -- Regex patterns, deduplicated across every bundle --\n" + "\n".join(lines) + "\n"
            written.append(self._write(index, shared, results, ("zod", "shared"), sorted(shared), output_dir, prelude))

        for bundle in bundles:
            roots = index.roots[bundle.name]
            owned = [n for n in index.defs if index.owning_bundle(n) == bundle.name]
            support = sorted(n for n in owned if n not in roots)
            if support:
                written.append(self._write(index, shared, results, ("zod", bundle.name, "support"), support, output_dir))
            for name in roots:
                written.append(self._write(index, shared, results, ("zod", bundle.name, name), [name], output_dir))

        return written

    def _write(self, index, shared, results: dict[str, ZodResult], file_parts, def_names, output_dir, prelude: str = "") -> Path:
        local = set(def_names)
        refs: set[str] = set()
        pattern_names: set[str] = set()
        for n in def_names:
            refs |= results[n].def_refs
            pattern_names |= results[n].pattern_names
        is_shared = file_parts == ("zod", "shared")

        schema_imports: dict[str, list[str]] = {}
        for ref in sorted(refs - local):
            schema_imports.setdefault(import_specifier(file_parts, _loc(ref, index, shared)), []).append(f"{ref}Schema")

        imports = ["/* eslint-disable @typescript-eslint/naming-convention */","/* eslint-disable @typescript-eslint/no-inferrable-types */","/* eslint-disable typedoc/require-exported-doc-comment */","import { z } from 'zod';"]
        if pattern_names and not is_shared:
            spec = import_specifier(file_parts, ("zod", "shared"))
            imports.append(f"import {{ {', '.join(sorted(pattern_names))} }} from '{spec}';")
        for spec, names in sorted(schema_imports.items()):
            imports.append(f"import {{ {', '.join(sorted(names))} }} from '{spec}';")

        body = [results[n].code for n in def_names]
        return write_file(output_dir, file_parts, TSFile(imports, prelude, body).render())
