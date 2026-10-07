import { DateTime } from "luxon";
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
