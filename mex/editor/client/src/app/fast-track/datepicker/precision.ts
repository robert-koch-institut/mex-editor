import { DateTime } from "luxon";

import {
  yearMonthDayPattern,
  yearMonthDayTimePattern,
  yearMonthPattern,
  yearPattern,
} from "../../shared/models/generated/shared";

/**
 * Precision for datepicker selection behaviour.
 */
export type DatepickerPrecision = "year" | "month" | "day" | "datetime";

/**
 * All precisions, ordered from coarse to fine.
 */
export const ALL_PRECISIONS: readonly DatepickerPrecision[] = ["year", "month", "day", "datetime"];

/**
 * Precision used while no value is set and no other precision is preferred.
 */
export const DEFAULT_PRECISION: DatepickerPrecision = "day";

/**
 * Most specific first, so a longer value never matches a shorter pattern.
 */
const PRECISION_REGEXES: readonly (readonly [DatepickerPrecision, RegExp])[] = [
  ["datetime", new RegExp(yearMonthDayTimePattern)],
  ["day", new RegExp(yearMonthDayPattern)],
  ["month", new RegExp(yearMonthPattern)],
  ["year", new RegExp(yearPattern)],
];

const TIME_PATTERN = /^(\d{2}):(\d{2})/;

/**
 * Detects the precision of a value string.
 * @param value Value string in one of the supported formats.
 * @returns The precision of the value or null if it matches no format.
 */
export function detectPrecision(value: string | null): DatepickerPrecision | null {
  if (!value) return null;
  return PRECISION_REGEXES.find(([, regex]) => regex.test(value))?.[0] ?? null;
}

/**
 * Picks the editing mode. A stored value always wins, even if its precision is not allowed,
 * so existing data is never rewritten silently. Otherwise the first allowed preference is used,
 * then {@link DEFAULT_PRECISION}, then the first allowed precision.
 * @param value Current value string.
 * @param preferred Preferred precisions, most important first.
 * @param allowed Precisions the user may choose from.
 * @returns The precision to edit in.
 */
export function resolvePrecision(
  value: string | null,
  preferred: readonly (DatepickerPrecision | null | undefined)[],
  allowed: readonly DatepickerPrecision[],
): DatepickerPrecision {
  const detected = detectPrecision(value);
  if (detected) return detected;
  const preference = preferred.find(
    (precision): precision is DatepickerPrecision =>
      precision != null && allowed.includes(precision),
  );
  if (preference) return preference;
  return allowed.includes(DEFAULT_PRECISION)
    ? DEFAULT_PRECISION
    : (allowed[0] ?? DEFAULT_PRECISION);
}

/**
 * Derives the precision from text typed into the date input. The current precision is tried first
 * and kept if the text fits it. Another precision is only taken if it is allowed.
 * @param text Text typed into the date input.
 * @param current Precision the datepicker is currently in.
 * @param allowed Precisions the user may choose from.
 * @param matches Tells whether the text is a valid date in the input format of a precision.
 * @returns The precision the text fits, or null if it fits none of the usable precisions.
 */
export function resolvePrecisionFromText(
  text: string,
  current: DatepickerPrecision,
  allowed: readonly DatepickerPrecision[],
  matches: (precision: DatepickerPrecision) => boolean,
): DatepickerPrecision | null {
  if (!text) return null;
  const candidates = [current, ...ALL_PRECISIONS.filter((precision) => precision !== current)];
  return (
    candidates.find(
      (precision) => (precision === current || allowed.includes(precision)) && matches(precision),
    ) ?? null
  );
}

/**
 * Parses a value string. All values are UTC, matching `useUtc: true` of the Luxon date adapter.
 * @param value Value string in one of the supported formats.
 * @returns The parsed date or null if the value is empty or invalid.
 */
export function parseValue(value: string | null): DateTime | null {
  if (!value || !detectPrecision(value)) return null;
  const parsed = DateTime.fromISO(value, { zone: "utc" });
  return parsed.isValid ? parsed : null;
}

/**
 * Serializes a date to the value string of the given precision.
 * @param date Date to serialize.
 * @param precision Precision of the resulting string.
 * @returns Value string.
 */
export function serializeValue(date: DateTime, precision: DatepickerPrecision): string {
  const utc = date.toUTC();
  switch (precision) {
    case "year":
      return utc.toFormat("yyyy");
    case "month":
      return utc.toFormat("yyyy-MM");
    case "day":
      return utc.toFormat("yyyy-MM-dd");
    case "datetime":
      return utc.toFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
  }
}

/**
 * Rebuilds a date in UTC from its calendar fields, cut to the given precision.
 * @param date Date to cut.
 * @param precision Precision to cut to.
 * @param time Time of day (HH:mm), only used for the datetime precision.
 * @returns The normalized UTC date.
 */
export function applyPrecision(
  date: DateTime,
  precision: DatepickerPrecision,
  time = "",
): DateTime {
  const { year, month, day } = date;
  switch (precision) {
    case "year":
      return DateTime.utc(year);
    case "month":
      return DateTime.utc(year, month);
    case "day":
      return DateTime.utc(year, month, day);
    case "datetime": {
      const [, hour = "0", minute = "0"] = TIME_PATTERN.exec(time) ?? [];
      return DateTime.utc(year, month, day, Number(hour), Number(minute));
    }
  }
}
