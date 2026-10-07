// Runtime half of the pydantic <-> Zod equivalence check.
//
// Copied, together with the freshly generated schemas and the shared case
// corpus, into a throwaway fixture dir by test_zod_runtime_equivalence.py.
// Every case here is the *same* case the Python half feeds to pydantic, so a
// mistranslation in the generator shows up as a disagreement between the two.

import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";
import type { ZodType } from "zod";

import * as organization from "./organization";
import * as person from "./person";

interface Case {
  description: string;
  payload: unknown;
  valid: boolean;
}

interface Group {
  model: string;
  module: string;
  schema: string;
  cases: Case[];
}

const modules: Record<string, Record<string, unknown>> = { organization, person };

const corpus = JSON.parse(
  readFileSync(join(import.meta.dirname, "cases.json"), "utf-8"),
) as Group[];

for (const group of corpus) {
  describe(group.model, () => {
    const schema = modules[group.module][group.schema] as ZodType;

    it("exports the generated schema the corpus names", () => {
      expect(schema, `${group.schema} missing from ${group.module}.ts`).toBeDefined();
    });

    for (const testCase of group.cases) {
      it(testCase.description, () => {
        expect(schema.safeParse(testCase.payload).success).toBe(testCase.valid);
      });
    }
  });
}
