import type z from "zod";

import type { ReferenceType } from "./zod-reference";

const recommendedKey = "recommended";
const referenceTypesKey = "referenceTypes";

interface MexMeta {
  [recommendedKey]?: boolean;
  [referenceTypesKey]?: ReferenceType[];
}

declare module "zod" {
  interface GlobalMeta {
    [recommendedKey]?: boolean;
    [referenceTypesKey]?: ReferenceType[];
  }
}

/**
 * Sets mex specific meta on the given schema and ensures to keep mex meta values.
 * @param schema The schema to add the meta to.
 * @param value The new value for mex meta.
 * @returns The new schema with given meta.
 */
export function mexMeta<T extends z.ZodType>(schema: T, value: MexMeta) {
  if (Object.values(value).length === 0) return schema;

  const sourceMeta = schema.meta();
  return schema.meta({ ...sourceMeta, ...value });
}
