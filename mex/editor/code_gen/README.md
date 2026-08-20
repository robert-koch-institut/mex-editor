# mex_form_codegen

Generates real Zod schemas (validation + inferred TypeScript types, in one
place) from mex-common pydantic models, for Angular Signal Forms. Resolves
fields from the actual Python type annotations (`pytypes.py`), not
`model.model_json_schema()`, since the two disagree for enough fields
(`Literal` discriminators, `VocabularyEnum`, `TemporalEntity`) to matter.

One generator, one file (`generate.py`), flat output, no plugin machinery.

## Setup

```bash
pip install mex-common --break-system-packages
```

## Run

```python
from mex.common.models import ExtractedActivity, MergedActivity, ActivityRuleSetResponse
from mex_form_codegen import Bundle, generate_zod_schemas

bundles = [Bundle(name="Activity", models=[ExtractedActivity, MergedActivity, ActivityRuleSetResponse])]
generate_zod_schemas(bundles, "out")
```

Or `python examples/generate_all_entities.py` for the full six-entity set.
Re-running after a model change just overwrites everything -- every file
has an `// AUTO-GENERATED ... do not edit by hand.` header, nothing
incremental.

## Output layout

Flat, kebab-case filenames, no subfolders:

```
shared.ts        # patterns + schemas for defs used by >1 bundle
form-schemas.ts   # Angular Signal Forms adapters + one FormSchema export per entity
{bundle-name}.ts   # everything that bundle owns: requested root models +
                    # whatever they need internally (bases, enums, rule sub-models)
```

Every field matches its source pydantic model strictly -- no relaxations
(a reference to another model requires that model's schema, not a bare
string). Every file starts with `/* eslint-disable
@typescript-eslint/naming-convention */` (needed for names like `$type`)
and every export has a `/** ... */` doc comment. Declarations within a
file are topologically sorted (`const` isn't hoisted in JS -- a forward
reference throws at runtime, not just a lint warning).

## Using the generated schemas in Angular Signal Forms

```ts
import { extractedActivityFormSchema } from "./form-schemas";
const activityForm = form(activitySignal, extractedActivityFormSchema);
```

`form-schemas.ts` holds two adapters plus one `...FormSchema` export per
entity, kept separate so the bundle files stay pure Zod:

- `validateWithZod(path, zodSchema)` -- runs a Zod schema against a
  Signal Forms field path, reports Zod issues as Signal Forms errors.
- `zodFormSchema(zodSchema)` -- wraps that for `schema<T>(...)`.

## Adding a bundle

```python
Bundle(name="Person", models=[ExtractedPerson, MergedPerson, PersonRuleSetResponse])
```

A type referenced by more than one bundle is auto-deduplicated into
`shared.ts`.

## Testing

`tests/test_codegen.py` -- pure Python, no external tools.

`tests/test_cross_validation.py` -- generates real schemas and runs the
exact same data through both `Model.model_validate(...)` and
`{Model}Schema.safeParse(...)` (via `npx tsx`), asserting they agree.
Needs a one-time `cd tests/js && npm install`; skipped automatically if
that's not set up.

## Module map

| File | What it does |
|---|---|
| `bundle.py` | `Bundle` -- a name + list of pydantic models |
| `pytypes.py` | Resolves a pydantic annotation into a small type IR |
| `schema_collect.py` | Builds the `SchemaIndex` from a bundle list |
| `patterns.py` | Dedupes regex patterns into named constants |
| `generate.py` | Type IR -> Zod schemas, file layout, `generate_zod_schemas()` |
