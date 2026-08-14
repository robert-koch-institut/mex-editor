"""AI-generated codegen module (Claude). Compact by design.

Writes validation/shared{SUFFIX} (patterns + runtime helpers + validators
for defs used by >1 bundle) and, per bundle, one
validation/{Bundle}/{EntityModel}{SUFFIX} per *requested* root model, plus
a single validation/{Bundle}/support{SUFFIX} bundling everything else that
bundle needs internally (factored-out bases, enums, rule sub-models) --
only real entity types get their own file.
"""
from __future__ import annotations
import json
from pathlib import Path
from ..bundle import Bundle
from ..patterns import PatternRegistry
from ..schema_collect import SchemaIndex
from ..ts_validators import GenResult, generate_def_validator
from ..ts_writer import TSFile, render_runtime_helpers
from .base import Generator, import_specifier, write_file


def _model_loc(name: str, index: SchemaIndex, shared: set[str]) -> tuple[str, ...]:
    return ("models", "shared") if name in shared else ("models", index.owning_bundle(name))


def _validator_loc(name: str, index: SchemaIndex, shared: set[str]) -> tuple[str, ...]:
    if name in shared:
        return ("validation", "shared")
    owner = index.owning_bundle(name)
    return ("validation", owner, name) if name in index.roots[owner] else ("validation", owner, "support")


class AngularSignalFormValidatorGenerator(Generator):
    name = "angular-signal-form-validators"

    def generate(self, index: SchemaIndex, bundles: list[Bundle], output_dir: Path) -> list[Path]:
        shared = index.shared_defs()
        patterns = PatternRegistry()
        gen = {n: generate_def_validator(n, e, patterns) for n, e in index.defs.items()}
        written: list[Path] = []

        all_patterns = {p for r in gen.values() for p in r.pattern_names}
        all_runtime = {p for r in gen.values() for p in r.runtime_fns}
        if shared or all_patterns or all_runtime:
            prelude = []
            if all_patterns:
                lines = [f"export const {n}: string = {json.dumps(p)};" for p, n in sorted(patterns.all_patterns().items(), key=lambda kv: kv[1]) if n in all_patterns]
                prelude.append("// -- Regex patterns, deduplicated across every bundle --\n" + "\n".join(lines) + "\n")
            if all_runtime:
                prelude.append(render_runtime_helpers(any_of_pattern="anyOfPatternValidator" in all_runtime, enum="enumValidator" in all_runtime))
            written.append(self._write(index, shared, gen, ("validation", "shared"), sorted(shared), output_dir,
                                        prelude="\n".join(prelude), extra_signals={"validate"} if all_runtime else set()))

        for bundle in bundles:
            roots = index.roots[bundle.name]
            owned = [n for n in index.defs if index.owning_bundle(n) == bundle.name]
            support = sorted(n for n in owned if n not in roots)
            if support:
                written.append(self._write(index, shared, gen, ("validation", bundle.name, "support"), support, output_dir))
            for name in roots:
                written.append(self._write(index, shared, gen, ("validation", bundle.name, name), [name], output_dir, roots={name}))

        return written

    def _write(self, index, shared, gen: dict[str, GenResult], file_parts, def_names, output_dir,
               *, roots: set[str] = frozenset(), prelude: str = "", extra_signals: set[str] | None = None) -> Path:
        signals, runtime, pat_names, refs = set(extra_signals or ()), set(), set(), set()
        for n in def_names:
            r = gen[n]
            signals |= r.signals_forms_fns
            runtime |= r.runtime_fns
            pat_names |= r.pattern_names
            refs |= r.referenced_defs

        local = set(def_names)
        is_shared = file_parts == ("validation", "shared")

        fn_imports: dict[str, list[str]] = {}
        for ref in sorted(refs - local):
            fn_imports.setdefault(import_specifier(file_parts, _validator_loc(ref, index, shared)), []).append(f"validate{ref}")

        type_imports: dict[str, list[str]] = {}
        for n in sorted(local | refs):
            type_imports.setdefault(import_specifier(file_parts, _model_loc(n, index, shared)), []).append(n)

        imports = ["import type { SchemaPath, SchemaPathTree } from '@angular/forms/signals';"]
        imports.append(f"import {{ schema, {', '.join(sorted(signals))} }} from '@angular/forms/signals';" if signals
                        else "import { schema } from '@angular/forms/signals';")
        if (runtime or pat_names) and not is_shared:
            imports.append(f"import {{ {', '.join(sorted(runtime | pat_names))} }} from '{import_specifier(file_parts, ('validation', 'shared'))}';")
        for spec, names in sorted(fn_imports.items()):
            imports.append(f"import {{ {', '.join(sorted(names))} }} from '{spec}';")
        for spec, names in sorted(type_imports.items()):
            imports.append(f"import type {{ {', '.join(sorted(names))} }} from '{spec}';")

        body = []
        for n in def_names:
            body.append(gen[n].field_function)
            if n in roots:
                var = n[0].lower() + n[1:]
                body.append(f"export const {var}Schema = schema<{n}>(validate{n});\n\n")

        return write_file(output_dir, file_parts, TSFile(imports, prelude, body).render())
