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
 * LuxonDateTime and nullable as zod type.
 */
export const luxonDateTimeNullabeSchema = () =>
  z
    .custom<DateTime | null>((val) => val == null || DateTime.isDateTime(val), {
      error: "validation.invalidDate", // null/undefined → leeres Feld
    })
    .nullable();
