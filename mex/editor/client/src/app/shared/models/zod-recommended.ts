import type { ZodType } from "zod";

import { mexMeta } from "./zod-mex-meta";

/**
 * Marks the given fieldSchema as recommended.
 * @param fieldSchema The field to mark as recommended.
 */
export function recommended<T extends ZodType>(fieldSchema: T): T {
  return mexMeta(fieldSchema, { recommended: true });
}

/**
 * Marks the given fieldSchema as recommended.
 * @param fieldSchema The field to mark as recommended.
 * @returns Returns true if the given field is recommended; otherwise false.
 */
export function isRecommended<T extends ZodType>(fieldSchema: T): boolean {
  return !!fieldSchema.meta()?.recommended;
}
