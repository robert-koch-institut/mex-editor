import { DateTime } from "luxon";
import { vi } from "vitest";

import type { DatepickerPrecision } from "./precision";
import {
  applyPrecision,
  detectPrecision,
  parseValue,
  resolvePrecision,
  resolvePrecisionFromText,
  serializeValue,
} from "./precision";

const SAMPLES: [DatepickerPrecision, string][] = [
  ["year", "2026"],
  ["month", "2026-03"],
  ["day", "2026-03-15"],
  ["datetime", "2026-03-15T10:30:00Z"],
];

const ALL: DatepickerPrecision[] = ["year", "month", "day", "datetime"];

describe("detectPrecision", () => {
  it.each(SAMPLES)("detects %s", (precision, value) => {
    expect(detectPrecision(value)).toBe(precision);
  });

  it.each([null, "", "not a date", "2026-13", "2026-03-32"])("returns null for %j", (value) => {
    expect(detectPrecision(value)).toBeNull();
  });
});

describe("parseValue / serializeValue", () => {
  it.each(SAMPLES)("round-trips %s in UTC", (precision, value) => {
    const parsed = parseValue(value);

    expect(parsed?.zoneName).toBe("UTC");
    expect(parsed && serializeValue(parsed, precision)).toBe(value);
  });

  it.each(SAMPLES)("serializes %s so that the generated pattern accepts it", (precision) => {
    const serialized = serializeValue(DateTime.utc(2026, 3, 15, 10, 30), precision);

    expect(detectPrecision(serialized)).toBe(precision);
  });

  it("returns null for null and unparsable values", () => {
    expect(parseValue(null)).toBeNull();
    expect(parseValue("garbage")).toBeNull();
  });
});

describe("applyPrecision", () => {
  const picked = DateTime.utc(2026, 3, 15, 10, 30, 45);

  it.each([
    ["year", "2026-01-01T00:00:00.000Z"],
    ["month", "2026-03-01T00:00:00.000Z"],
    ["day", "2026-03-15T00:00:00.000Z"],
  ] as const)("cuts to %s", (precision, expected) => {
    expect(applyPrecision(picked, precision).toISO()).toBe(expected);
  });

  it("applies the given time for datetime and drops seconds", () => {
    expect(applyPrecision(picked, "datetime", "12:45").toISO()).toBe("2026-03-15T12:45:00.000Z");
  });

  it.each(["", "garbage"])("falls back to 00:00 for time %j", (time) => {
    expect(applyPrecision(picked, "datetime", time).toISO()).toBe("2026-03-15T00:00:00.000Z");
  });
});

describe("resolvePrecision", () => {
  it("lets a stored value win, even if its precision is not allowed", () => {
    expect(resolvePrecision("2026-03-15", ["year"], ["year"])).toBe("day");
  });

  it("uses the first preference that is allowed", () => {
    expect(resolvePrecision(null, [undefined, "month"], ALL)).toBe("month");
    expect(resolvePrecision(null, ["day", "month"], ["month", "year"])).toBe("month");
  });

  it("falls back to day when it is allowed", () => {
    expect(resolvePrecision(null, [], ALL)).toBe("day");
    expect(resolvePrecision(null, [null], ALL)).toBe("day");
  });

  it("falls back to the first allowed precision when day is not allowed", () => {
    expect(resolvePrecision(null, [], ["year", "month"])).toBe("year");
  });
});

describe("resolvePrecisionFromText", () => {
  const fits =
    (...precisions: DatepickerPrecision[]) =>
    (precision: DatepickerPrecision) =>
      precisions.includes(precision);

  it("returns null for empty text without asking for matches", () => {
    const matches = vi.fn(() => true);

    expect(resolvePrecisionFromText("", "day", ALL, matches)).toBeNull();
    expect(matches).not.toHaveBeenCalled();
  });

  it("keeps the current precision when the text fits it", () => {
    expect(resolvePrecisionFromText("x", "datetime", ALL, fits("day", "datetime"))).toBe(
      "datetime",
    );
    expect(resolvePrecisionFromText("x", "year", ALL, fits("year", "month"))).toBe("year");
  });

  it("switches to another allowed precision the text fits", () => {
    expect(resolvePrecisionFromText("x", "day", ALL, fits("year"))).toBe("year");
    expect(resolvePrecisionFromText("x", "year", ALL, fits("month"))).toBe("month");
  });

  it("prefers day over datetime, because both share the input format", () => {
    expect(resolvePrecisionFromText("x", "year", ALL, fits("day", "datetime"))).toBe("day");
  });

  it("falls back to datetime when day is not allowed", () => {
    expect(
      resolvePrecisionFromText("x", "year", ["year", "datetime"], fits("day", "datetime")),
    ).toBe("datetime");
  });

  it("never switches to a precision that is not allowed", () => {
    expect(resolvePrecisionFromText("x", "day", ["day", "datetime"], fits("year"))).toBeNull();
  });

  it("keeps a current precision that is not allowed when the text fits it", () => {
    expect(resolvePrecisionFromText("x", "day", ["year"], fits("day"))).toBe("day");
  });

  it("returns null when the text fits nothing", () => {
    expect(resolvePrecisionFromText("x", "day", ALL, fits())).toBeNull();
  });
});
