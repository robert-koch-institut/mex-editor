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

/**
 * FieldKind API documentation.
 */
export type FieldKind =
  "string" | "number" | "boolean" | "date" | "enum" | "object" | "array" | "unknown";

const WRAPPERS = new Set([
  "optional",
  "nullable",
  "default",
  "prefault",
  "readonly",
  "catch",
  "nonoptional",
]);

/** Entfernt optional/nullable/default/... bis zum eigentlichen Typ (zod 4: def.type / def.innerType). */
export function unwrapZod(schema: z.ZodType): z.ZodType {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let s: any = schema;
  while (WRAPPERS.has(s.def.type)) s = s.def.innerType;
  return s;
}

/**
 * getFieldKind API documentation.
 */
export function getFieldKind(schema: z.ZodType): FieldKind {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const type = (unwrapZod(schema) as any).def.type as string;
  switch (type) {
    case "string":
    case "number":
    case "boolean":
    case "date":
    case "enum":
    case "object":
    case "array":
      return type;
    default:
      return "unknown";
  }
}
