import { DateTime } from "luxon";
import type { ZodType } from "zod";
import z from "zod";

/**
 * LuxonDateTime as zod type.
 */
export const luxonDateTimeSchema = () =>
  z
    .custom<DateTime>((val) => DateTime.isDateTime(val), {
      error: "validation.required", // null/undefined → leeres Feld
    })
    .refine((val) => val.isValid, {
      error: "validation.invalidDate", // Instanz vorhanden, aber Parse fehlgeschlagen
    });

/**
 * Nullable LuxonDateTime as zod type.
 */
export const luxonDateTimeNullableSchema = () =>
  z
    .custom<DateTime | null>((val) => val == null || DateTime.isDateTime(val), {
      error: "validation.invalidDate",
    })
    .refine((val) => (DateTime.isDateTime(val) ? val.isValid : val == null), {
      error: "validation.invalidDate",
    })
    .nullable();

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
 */
export function isRecommended<T extends ZodType>(fieldSchema: T): boolean {
  const meta = fieldSchema.meta();
  return !!meta && recommendFieldMetaKey in meta && !!meta[recommendFieldMetaKey];
}
