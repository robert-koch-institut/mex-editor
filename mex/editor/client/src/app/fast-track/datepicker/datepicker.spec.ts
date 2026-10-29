import { signal } from "@angular/core";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import type { FieldState, FieldTree } from "@angular/forms/signals";
import type { MatDateFormats } from "@angular/material/core";
import { ErrorStateMatcher } from "@angular/material/core";
import { MatDatepickerInput } from "@angular/material/datepicker";
import { By } from "@angular/platform-browser";
import type { TranslateParams } from "@jsverse/transloco";
import { TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";
import { vi } from "vitest";

import { Datepicker, DatepickerErrorStateMatcher, PrecisionDateFormats } from "./datepicker";
import type { DatepickerPrecision } from "./precision";
import { PrecisionMenu } from "./precision-menu";

/*
 * Notes:
 *
 * - Providers (UTC Luxon adapter, `DynamicLuxonFormats`, transloco with preloaded `de`/`en`)
 *   come from `src/test-providers.ts`. German is the default language: dates are typed as
 *   `dd.MM.yyyy`, English uses `MM/dd/yyyy`.
 * - `translate` is mocked to return the key, so texts are independent of the translation files.
 *   The language itself is steered with `TranslocoService.setActiveLang()`.
 * - `formField` is a required host-directive input and must be set before the first detectChanges().
 */

function fakeFieldTree(state: { errors?: unknown[]; touched?: boolean } = {}) {
  const fieldState = {
    errors: () => state.errors ?? [],
    invalid: () => (state.errors ?? []).length > 0,
    touched: () => state.touched ?? false,
  };
  return (() => fieldState) as unknown as FieldTree<unknown>;
}

function typeInto(input: HTMLInputElement, text: string) {
  input.value = text;
  input.dispatchEvent(new Event("input"));
  input.dispatchEvent(new Event("blur"));
}

// eslint-disable-next-line max-lines-per-function
describe("Datepicker", () => {
  let fixture: ComponentFixture<Datepicker>;
  let component: Datepicker;
  let transloco: TranslocoService;

  const dateInput = () =>
    fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
  const timeInput = () =>
    fixture.debugElement.query(By.css("input[type=time]"))?.nativeElement as
      HTMLInputElement | undefined;
  const menu = () => fixture.debugElement.query(By.directive(PrecisionMenu));
  const errorHint = () => fixture.debugElement.query(By.css(".error-hint"));

  async function settle() {
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
  }

  async function create(inputs: Record<string, unknown> = {}) {
    fixture = TestBed.createComponent(Datepicker);
    component = fixture.componentInstance;
    fixture.componentRef.setInput("formField", fakeFieldTree());
    for (const [name, value] of Object.entries(inputs)) {
      fixture.componentRef.setInput(name, value);
    }
    await settle();
  }

  async function type(text: string) {
    typeInto(dateInput(), text);
    await settle();
  }

  async function setTime(text: string) {
    const input = timeInput();
    assert(input);
    input.value = text;
    input.dispatchEvent(new Event("input"));
    await settle();
  }

  async function selectPrecision(precision: DatepickerPrecision) {
    menu().componentInstance.precisionSelected.emit(precision);
    await settle();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Datepicker],
    }).compileComponents();

    transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("de");
    vi.spyOn(transloco, "translate").mockImplementation((key: TranslateParams) => key as string);
  });

  afterEach(() => {
    transloco.setActiveLang("de");
    vi.restoreAllMocks();
  });

  it("creates with a null value by default", async () => {
    await create();

    expect(component.value()).toBeNull();
  });

  describe("day precision (default)", () => {
    it("writes a typed date as ISO day string", async () => {
      await create();

      await type("15.03.2026");

      expect(component.value()).toBe("2026-03-15");
    });

    it("shows an existing value in the display format", async () => {
      await create({ value: "2026-03-15" });

      expect(dateInput().value).toBe("15.03.2026");
    });

    it("writes null when the text is cleared", async () => {
      await create({ value: "2026-03-15" });

      await type("");

      expect(component.value()).toBeNull();
    });

    it("has no time field", async () => {
      await create();

      expect(timeInput()).toBeUndefined();
    });
  });

  describe("year and month precision", () => {
    it("writes a typed year", async () => {
      await create({ precision: "year" });

      expect(dateInput().placeholder).toBe("yyyy");

      await type("2026");

      expect(component.value()).toBe("2026");
    });

    it("writes a typed month in the format of the active language", async () => {
      await create({ precision: "month" });
      expect(dateInput().placeholder).toBe("MM.yyyy");

      await type("03.2026");
      expect(component.value()).toBe("2026-03");

      transloco.setActiveLang("en");
      await settle();
      expect(dateInput().placeholder).toBe("MM/yyyy");

      await type("04/2026");
      expect(component.value()).toBe("2026-04");
    });

    it("derives the mode from an existing value, ignoring the precision input", async () => {
      await create({ value: "2026", precision: "day" });

      expect(dateInput().value).toBe("2026");
    });
  });

  describe("datetime precision", () => {
    it("shows date and time (UTC) of an existing value", async () => {
      await create({ value: "2026-03-15T10:30:00Z" });

      expect(dateInput().value).toBe("15.03.2026");
      expect(timeInput()?.value).toBe("10:30");
    });

    it("keeps the date when the time changes, without a timezone shift", async () => {
      await create({ value: "2026-03-15T10:30:00Z" });

      await setTime("12:45");

      expect(component.value()).toBe("2026-03-15T12:45:00Z");
    });

    it("keeps the time when the date changes", async () => {
      await create({ value: "2026-03-15T10:30:00Z" });

      await type("20.03.2026");

      expect(component.value()).toBe("2026-03-20T10:30:00Z");
    });

    it("waits for a date when only a time was entered", async () => {
      await create({ precision: "datetime" });

      await setTime("08:15");
      expect(component.value()).toBeNull();

      await type("15.03.2026");
      expect(component.value()).toBe("2026-03-15T08:15:00Z");
    });
  });

  describe("precision selection", () => {
    it("is shown when more than one precision is allowed", async () => {
      await create();

      expect(menu()).not.toBeNull();
    });

    it("is placed in the prefix of the form field", async () => {
      await create();

      const prefix = fixture.debugElement.query(By.css(".mat-mdc-form-field-icon-prefix"));
      expect(prefix.query(By.directive(PrecisionMenu))).not.toBeNull();
    });

    it("is hidden when only one precision is allowed", async () => {
      await create({ allowedPrecisions: ["day"] });

      expect(menu()).toBeNull();
    });

    it("offers only the allowed precisions", async () => {
      await create({ allowedPrecisions: ["month", "day"] });

      expect(menu().componentInstance.options()).toStrictEqual(["month", "day"]);
    });

    it("cuts the value when switching to a coarser precision", async () => {
      await create({ value: "2026-03-15" });

      await selectPrecision("month");
      expect(component.value()).toBe("2026-03");
      expect(dateInput().value).toBe("03.2026");

      await selectPrecision("year");
      expect(component.value()).toBe("2026");
      expect(dateInput().value).toBe("2026");
    });

    it("fills with the start of the period when switching to a finer precision", async () => {
      await create({ value: "2026" });

      await selectPrecision("day");

      expect(component.value()).toBe("2026-01-01");
    });

    it("shows the time field after switching to datetime", async () => {
      await create({ value: "2026-03-15" });

      await selectPrecision("datetime");

      expect(component.value()).toBe("2026-03-15T00:00:00Z");
      expect(timeInput()?.value).toBe("00:00");
    });

    it("ignores a precision that is not allowed", async () => {
      await create({ value: "2026-03", allowedPrecisions: ["year", "month"] });

      await selectPrecision("day");

      expect(component.value()).toBe("2026-03");
    });

    it("keeps the precision of an existing value even if it is not allowed", async () => {
      await create({ value: "2026-03-15", allowedPrecisions: ["year", "month"] });

      expect(dateInput().value).toBe("15.03.2026");
    });

    it("starts with day when it is allowed and nothing else is preferred", async () => {
      await create();

      expect(dateInput().placeholder).toBe("dd.MM.yyyy");
    });

    it("starts with the first allowed precision when day is not allowed", async () => {
      await create({ allowedPrecisions: ["year", "month"] });

      expect(dateInput().placeholder).toBe("yyyy");
    });

    it("is disabled when the datepicker is disabled or readonly", async () => {
      await create({ disabled: true });
      expect(menu().componentInstance.disabled()).toBe(true);

      fixture.componentRef.setInput("disabled", false);
      fixture.componentRef.setInput("readonly", true);
      await settle();
      expect(menu().componentInstance.disabled()).toBe(true);
    });
  });

  describe("precision from typed text", () => {
    const currentPrecision = () => menu().componentInstance.precision();

    it("switches to year when a year is typed", async () => {
      await create();

      await type("2026");

      expect(currentPrecision()).toBe("year");
      expect(component.value()).toBe("2026");
      expect(dateInput().value).toBe("2026");
      expect(dateInput().placeholder).toBe("yyyy");
      expect(errorHint()).toBeNull();
    });

    it("switches to month when a month is typed, in the format of the active language", async () => {
      await create();
      await type("03.2026");
      expect(currentPrecision()).toBe("month");
      expect(component.value()).toBe("2026-03");

      transloco.setActiveLang("en");
      await settle();
      await create();
      await type("04/2026");

      expect(currentPrecision()).toBe("month");
      expect(component.value()).toBe("2026-04");
    });

    it("switches to day when a full date is typed in year mode", async () => {
      await create({ precision: "year" });

      await type("15.03.2026");

      expect(currentPrecision()).toBe("day");
      expect(component.value()).toBe("2026-03-15");
      expect(dateInput().placeholder).toBe("dd.MM.yyyy");
    });

    it("replaces an existing value of another precision", async () => {
      await create({ value: "2026-03-15" });

      await type("2027");

      expect(currentPrecision()).toBe("year");
      expect(component.value()).toBe("2027");
    });

    it("keeps datetime when a full date is typed", async () => {
      await create({ value: "2026-03-15T10:30:00Z" });

      await type("20.03.2026");

      expect(currentPrecision()).toBe("datetime");
      expect(component.value()).toBe("2026-03-20T10:30:00Z");
      expect(timeInput()).toBeDefined();
    });

    it("leaves datetime and hides the time field when a year is typed", async () => {
      await create({ value: "2026-03-15T10:30:00Z" });

      await type("2027");

      expect(currentPrecision()).toBe("year");
      expect(component.value()).toBe("2027");
      expect(timeInput()).toBeUndefined();
    });

    it("takes datetime when day is not allowed and a full date is typed", async () => {
      await create({ allowedPrecisions: ["year", "datetime"], precision: "year" });

      await type("15.03.2026");

      expect(currentPrecision()).toBe("datetime");
      expect(component.value()).toBe("2026-03-15T00:00:00Z");
      expect(timeInput()?.value).toBe("00:00");
    });

    it("does not switch to a precision that is not allowed", async () => {
      await create({ allowedPrecisions: ["day", "datetime"] });

      await type("2026");

      expect(currentPrecision()).toBe("day");
      expect(dateInput().placeholder).toBe("dd.MM.yyyy");
    });

    it("does not switch while the text is incomplete", async () => {
      await create();

      await type("15.03.20");

      expect(currentPrecision()).toBe("day");
      expect(component.value()).toBeNull();
      expect(errorHint()).not.toBeNull();
    });

    it("does not switch when the text is cleared", async () => {
      await create({ value: "2026" });

      await type("");

      expect(currentPrecision()).toBe("year");
      expect(component.value()).toBeNull();
      expect(errorHint()).toBeNull();
    });

    it("clears an earlier parse error once the text fits another allowed precision", async () => {
      await create();
      await type("not a date");
      expect(errorHint()).not.toBeNull();

      await type("2026");

      expect(errorHint()).toBeNull();
    });
  });

  describe("parse errors", () => {
    it("flags a parse error and shows the hint for unparsable text", async () => {
      await create();

      await type("not a date");

      expect(errorHint()).not.toBeNull();
    });

    it("does not flag a parse error for empty input", async () => {
      await create();

      await type("");

      expect(errorHint()).toBeNull();
    });

    it("clears the parse error once the text becomes valid", async () => {
      await create();
      await type("not a date");
      expect(errorHint()).not.toBeNull();

      await type("15.03.2026");

      expect(errorHint()).toBeNull();
    });

    it("names the expected format in the hint", async () => {
      await create({ precision: "year" });
      const translate = vi.mocked(transloco.translate);

      await type("abcd");

      expect(translate).toHaveBeenCalledWith(
        "datepicker.validation.parse",
        { format: "yyyy" },
        expect.anything(),
      );
    });
  });

  describe("inputs and outputs", () => {
    it("reflects disabled on the native elements", async () => {
      await create({ value: "2026-03-15T10:30:00Z", disabled: true });

      expect(dateInput().disabled).toBe(true);
      expect(timeInput()?.disabled).toBe(true);
    });

    it("reflects readonly on the native elements", async () => {
      await create({ value: "2026-03-15T10:30:00Z", readonly: true });

      expect(dateInput().readOnly).toBe(true);
      expect(timeInput()?.readOnly).toBe(true);
    });

    it("passes minDate and maxDate to the datepicker input", async () => {
      const min = DateTime.utc(2020, 1, 1);
      const max = DateTime.utc(2030, 1, 1);
      await create({ minDate: min, maxDate: max });

      const picker = fixture.debugElement
        .query(By.directive(MatDatepickerInput))
        .injector.get(MatDatepickerInput);
      expect(picker.min).toBe(min);
      expect(picker.max).toBe(max);
    });

    it("emits touch on blur of the date and the time input", async () => {
      await create({ precision: "datetime" });
      const touchSpy = vi.fn();
      component.touch.subscribe(touchSpy);

      dateInput().dispatchEvent(new Event("blur"));
      timeInput()?.dispatchEvent(new Event("blur"));

      expect(touchSpy).toHaveBeenCalledTimes(2);
    });

    it("does not let clicks in the time field reach the form field", async () => {
      await create({ precision: "datetime" });
      const click = new MouseEvent("click", { bubbles: true });
      const stop = vi.spyOn(click, "stopPropagation");

      timeInput()?.dispatchEvent(click);

      expect(stop).toHaveBeenCalled();
    });

    it("focus() delegates to the native input", async () => {
      await create();
      const focusSpy = vi.spyOn(dateInput(), "focus");

      component.focus();

      expect(focusSpy).toHaveBeenCalled();
    });
  });

  describe("language change", () => {
    it("re-renders the shown date in the format of the new language", async () => {
      await create({ value: "2026-03-15" });
      expect(dateInput().value).toBe("15.03.2026");

      transloco.setActiveLang("en");
      await settle();

      expect(dateInput().value).toBe("03/15/2026");
      expect(component.value()).toBe("2026-03-15");
    });

    it("re-renders the placeholder and keeps the value for month precision", async () => {
      await create({ value: "2026-03" });

      transloco.setActiveLang("en");
      await settle();

      expect(dateInput().placeholder).toBe("MM/yyyy");
      expect(dateInput().value).toBe("03/2026");
      expect(component.value()).toBe("2026-03");
    });

    it("stays null when there was no value", async () => {
      await create();

      transloco.setActiveLang("en");
      await settle();

      expect(component.value()).toBeNull();
      expect(dateInput().value).toBe("");
    });
  });
});

describe("DatepickerErrorStateMatcher", () => {
  const hostState = { name: "host" } as unknown as FieldState<unknown>;

  function create(hasParseError: boolean, defaultState: boolean) {
    const defaultMatcher = {
      isErrorState: vi.fn(() => defaultState),
      isSignalErrorState: vi.fn(() => defaultState),
    };
    TestBed.configureTestingModule({
      providers: [{ provide: ErrorStateMatcher, useValue: defaultMatcher }],
    });
    const matcher = TestBed.runInInjectionContext(
      () => new DatepickerErrorStateMatcher(signal(hasParseError), signal(hostState)),
    );
    return { matcher, defaultMatcher };
  }

  it.each([
    [false, false, false],
    [true, false, true],
    [false, true, true],
    [true, true, true],
  ])(
    "parse error %s and host error state %s give signal error state %s",
    (hasParseError, defaultState, expected) => {
      const { matcher } = create(hasParseError, defaultState);

      expect(matcher.isSignalErrorState(null)).toBe(expected);
    },
  );

  it("asks the default matcher about the state of the host form field", () => {
    const { matcher, defaultMatcher } = create(false, false);

    matcher.isSignalErrorState(null);

    const [field] = defaultMatcher.isSignalErrorState.mock.calls[0] as unknown as [
      () => FieldState<unknown>,
    ];
    expect(field()).toBe(hostState);
  });

  it("delegates the classic error state to the default matcher only", () => {
    const { matcher } = create(true, false);

    expect(matcher.isErrorState(null, null)).toBe(false);
  });
});

const BASE: MatDateFormats = {
  parse: { dateInput: "dd.MM.yyyy" },
  display: {
    dateInput: "dd.MM.yyyy",
    monthYearLabel: "MMM yyyy",
    dateA11yLabel: "LL",
    monthYearA11yLabel: "MMMM yyyy",
  },
};

describe("PrecisionDateFormats", () => {
  let transloco: TranslocoService;

  function create(precision: DatepickerPrecision) {
    const formats = TestBed.runInInjectionContext(() => new PrecisionDateFormats(BASE));
    formats.bindPrecision(signal(precision));
    return formats;
  }

  beforeEach(() => {
    transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("de");
  });

  afterEach(() => {
    transloco.setActiveLang("de");
  });

  it.each(["day", "datetime"] as const)("keeps the base formats for %s", (precision) => {
    const formats = create(precision);

    expect(formats.parse).toBe(BASE.parse);
    expect(formats.display).toBe(BASE.display);
  });

  it("uses yyyy for year", () => {
    const formats = create("year");

    expect(formats.parse.dateInput).toBe("yyyy");
    expect(formats.display.dateInput).toBe("yyyy");
  });

  it("uses a language dependent format for month", () => {
    const formats = create("month");

    expect(formats.parse.dateInput).toBe("MM.yyyy");
    expect(formats.display.dateInput).toBe("MM.yyyy");

    transloco.setActiveLang("en");

    expect(formats.parse.dateInput).toBe("MM/yyyy");
    expect(formats.display.dateInput).toBe("MM/yyyy");
  });

  it("keeps the other display formats when overriding the input format", () => {
    const { display } = create("year");

    expect(display.monthYearLabel).toBe("MMM yyyy");
    expect(display.dateA11yLabel).toBe("LL");
    expect(display.monthYearA11yLabel).toBe("MMMM yyyy");
  });

  it.each([
    ["year", "de", "yyyy"],
    ["year", "en", "yyyy"],
    ["month", "de", "MM.yyyy"],
    ["month", "en", "MM/yyyy"],
    ["day", "de", "dd.MM.yyyy"],
    ["datetime", "en", "dd.MM.yyyy"],
  ] as const)(
    "formatFor(%s) in %s is %s, independent of the bound precision",
    (precision, lang, expected) => {
      transloco.setActiveLang(lang);
      const formats = create("day");

      expect(formats.formatFor(precision)).toBe(expected);
    },
  );

  it("follows the bound precision signal", () => {
    const precision = signal<DatepickerPrecision>("day");
    const formats = TestBed.runInInjectionContext(() => new PrecisionDateFormats(BASE));
    formats.bindPrecision(precision);

    expect(formats.parse.dateInput).toBe("dd.MM.yyyy");

    precision.set("year");

    expect(formats.parse.dateInput).toBe("yyyy");
  });
});
