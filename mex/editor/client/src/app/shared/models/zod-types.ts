import type { ZodType } from "zod";

/**
 * The key used inside zod meta to mark fields as recommended.
 */
export const recommendFieldMetaKey = "recommended";

/**
 * Marks the given fieldSchema as recommended.
 * @param fieldSchema The field to mark as recommended.
 */
export function recommended<T extends ZodType>(fieldSchema: T): T {
  return fieldSchema.meta({ [recommendFieldMetaKey]: true });
}

/**
 * Marks the given fieldSchema as recommended.
 * @param fieldSchema The field to mark as recommended.
 * @returns Returns true if the given field is recommended; otherwise false.
 */
export function isRecommended<T extends ZodType>(fieldSchema: T): boolean {
  const meta = fieldSchema.meta();
  return !!meta && recommendFieldMetaKey in meta && !!meta[recommendFieldMetaKey];
}
