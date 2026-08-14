# mex_form_codegen

Generates TypeScript from mex-common pydantic models: interfaces, Angular
Signal Forms validators, and (experimental) Zod schemas. Resolves fields
from the real Python type annotations (`pytypes.py`), not
`model.model_json_schema()` — the two disagree often enough (`Literal`
discriminators, `VocabularyEnum`, `TemporalEntity`) that trusting the
schema produced subtly wrong output.

## Setup

```bash
pip install mex-common --break-system-packages   # or your project's venv
```

No other dependencies — no Jinja, no npm packages needed to *run* this.
(The generated code imports `@angular/forms/signals` / `zod` at the
TypeScript/npm level, in whatever project you copy the output into.)

## Running it

```python
from mex.common.models import ExtractedActivity, MergedActivity, ActivityRuleSetResponse
from mex_form_codegen import Bundle, generate_typescript_interfaces, generate_angular_signal_form_validators

bundles = [Bundle(name="Activity", models=[ExtractedActivity, MergedActivity, ActivityRuleSetResponse])]

generate_typescript_interfaces(bundles, "out")            # out/model/...
generate_angular_signal_form_validators(bundles, "out")   # out/validation/...
```

Or see `examples/generate_all_entities.py` for the full six-entity set
(Resource, Activity, Person, ContactPoint, OrganizationalUnit,
Organization) — run it directly:

```bash
python examples/generate_all_entities.py
```

**Re-running after a model change**: just run it again. Every file is
regenerated from scratch each time (there's a `// AUTO-GENERATED ... do
not edit by hand.` header, and every file ends in `.generated.ts` so it's
easy to `.gitignore` or wire into a pre-build step). There's nothing
incremental to worry about — no stale state, no manual merge.

## Adding a bundle

A `Bundle` is just a name + a list of pydantic model classes:

```python
Bundle(name="Person", models=[ExtractedPerson, MergedPerson, PersonRuleSetResponse])
```

Any type referenced by more than one bundle (e.g. `Text`, `Link`) is
automatically deduplicated into a shared file instead of being repeated
per bundle — nothing to configure.

## Output layout

File and folder names are kebab-case (Angular's default convention) --
exported TS symbols inside stay PascalCase/camelCase as usual.

```
model/
  shared.generated.ts          # types used by >1 bundle
  {bundle-name}.generated.ts    # that bundle's own types
validation/
  shared.generated.ts           # validators + patterns for shared types
  {bundle-name}/
    {entity-model}.generated.ts  # one file per *requested* model (extracted-x, merged-x, ...)
    support.generated.ts         # everything else that bundle needs internally
                                  # (factored-out base classes, enums, rule sub-models)
zod/                            # same shape as validation/, from the Zod generator
```

Only the models you actually pass in `Bundle.models` get their own file.
Everything else the bundle needs (a shared base class two of your models
extend, an enum a field uses, ...) is collected into one `support.generated.ts`
per bundle — kept off the “one file per entity” list on purpose.

## Adding a new generator

A generator is a class with one method. It receives the `SchemaIndex`
already built from your bundles (every model/enum resolved once, shared
vs. bundle-owned already worked out) — it doesn't need to touch pydantic
at all.

```python
from pathlib import Path
from mex_form_codegen import Generator, run_generators, TypeScriptInterfaceGenerator

class MyGenerator(Generator):
    name = "my-format"

    def generate(self, index, bundles, output_dir: Path) -> list[Path]:
        written = []
        for def_name, entry in index.defs.items():
            ...  # entry is a ModelDef or EnumDef, see schema_collect.py
        return written

run_generators(bundles, "out", [TypeScriptInterfaceGenerator(), MyGenerator()])
```

See `generators/zod.py` for a complete example (an experimental generator
that ships real Zod schemas, not just types) and `generators/base.py` for
the shared `import_specifier()` helper if your generator also lays output
out in folders and needs relative imports between them.

## Module map

| File | What it does |
|---|---|
| `bundle.py` | `Bundle` — a name + list of pydantic models |
| `pytypes.py` | Resolves a pydantic annotation into a small type IR (object ref, enum ref, list, union, scalar, literal) |
| `schema_collect.py` | Walks a bundle's models via `pytypes`, builds the `SchemaIndex` (every def, which bundle(s) use it, factored-out shared bases) |
| `patterns.py` | Dedupes regex patterns into named constants (`identifierPattern`, `emailPattern`, ...) |
| `ts_types.py` | IR → TS interfaces / type aliases |
| `ts_validators.py` | IR → Angular Signal Forms validator functions |
| `ts_zod.py` | IR → Zod schemas (experimental) |
| `ts_writer.py` | Plain-Python string builders used by the above (no templating engine) |
| `generators/` | `Generator` base class + the three built-in generators |

All of the above is written compactly, not for human readability — it's
meant to be read alongside this README and edited directly rather than
treated as a black box. The code it *outputs* is the part that should
stay readable, since that's what ends up in your Angular project.
