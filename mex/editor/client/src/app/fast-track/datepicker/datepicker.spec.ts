import type { ElementRef } from "@angular/core";
import { signal } from "@angular/core";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import type { FieldState, FormField } from "@angular/forms/signals";
import type { MatDateFormats } from "@angular/material/core";
import { provideLuxonDateAdapter } from "@angular/material-luxon-adapter";
import { By } from "@angular/platform-browser";
import { TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";
import { vi } from "vitest";

import { Datepicker, ImmediateErrorStateMatcher } from "./datepicker";

/*
 * Assumption: Luxon date adapter (`.plus(0)` on the value in the
 * langChanges$ subscription is a Luxon DateTime method) — same assumption
 * used throughout this test suite.
 */

function setNativeValue(
  fixture: ComponentFixture<unknown>,
  input: HTMLInputElement,
  value: string,
) {
  input.value = value;
  input.dispatchEvent(new Event("input"));
  fixture.detectChanges();
}

// eslint-disable-next-line max-lines-per-function
describe("Datepicker", () => {
  let fixture: ComponentFixture<Datepicker>;
  let component: Datepicker;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Datepicker],
      providers: [provideLuxonDateAdapter()],
    }).compileComponents();

    fixture = TestBed.createComponent(Datepicker);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("creates with a null value by default", () => {
    expect(component.value()).toBeNull();
  });

  it("parses a typed date into the value", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "1/1/2026");
    input.dispatchEvent(new Event("blur"));
    fixture.detectChanges();

    expect(component.value()?.isValid).toBe(true);
    expect(component.value()?.toISODate()).toBe("2026-01-01");
  });

  it("flags a parse error and shows the hint for unparsable text", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "not a date");
    input.dispatchEvent(new Event("blur"));
    fixture.detectChanges();

    expect(component.customErrorMatcher.hasParseError()).toBe(true);
    expect(fixture.debugElement.query(By.css(".error-hint"))).not.toBeNull();
  });

  it("does not flag a parse error when the input is empty", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "");
    input.dispatchEvent(new Event("blur"));
    fixture.detectChanges();

    expect(component.customErrorMatcher.hasParseError()).toBe(false);
    expect(fixture.debugElement.query(By.css(".error-hint"))).toBeNull();
  });

  it("clears the parse error once a previously-invalid value becomes valid", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "not a date");
    input.dispatchEvent(new Event("blur"));
    fixture.detectChanges();
    expect(component.customErrorMatcher.hasParseError()).toBe(true);

    setNativeValue(fixture, input, "1/1/2026");
    input.dispatchEvent(new Event("blur"));
    fixture.detectChanges();

    expect(component.customErrorMatcher.hasParseError()).toBe(false);
  });

  it("reflects the disabled input on the native element", () => {
    fixture.componentRef.setInput("disabled", true);
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    expect(input.disabled).toBe(true);
  });

  it("reflects the readonly input on the native element", () => {
    fixture.componentRef.setInput("readonly", true);
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    expect(input.readOnly).toBe(true);
  });

  it("reflects minDate/maxDate inputs (shallow check — binding only, not enforced-range behavior)", () => {
    const min = DateTime.fromISO("2020-01-01");
    const max = DateTime.fromISO("2030-01-01");
    fixture.componentRef.setInput("minDate", min);
    fixture.componentRef.setInput("maxDate", max);
    fixture.detectChanges();

    expect(component.minDate()).toBe(min);
    expect(component.maxDate()).toBe(max);
  });

  it("emits touch on blur", () => {
    const touchSpy = vi.fn();
    component.touch.subscribe(touchSpy);

    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    input.dispatchEvent(new Event("blur"));

    expect(touchSpy).toHaveBeenCalled();
  });

  it("focus() delegates to the native input", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    const focusSpy = vi.spyOn(input, "focus");

    component.focus();

    expect(focusSpy).toHaveBeenCalled();
  });

  it("refreshes an existing value (new DateTime instance, same moment) when the language changes", () => {
    const initial = DateTime.fromISO("2026-01-01");
    component.value.set(initial);
    fixture.detectChanges();

    TestBed.inject(TranslocoService).setActiveLang("en");
    fixture.detectChanges();

    const refreshed = component.value();
    expect(refreshed).not.toBe(initial); // `.plus(0)` returns a new instance
    expect(refreshed?.toISO()).toBe(initial.toISO());
  });

  it("stays null on a language change when there was no value", () => {
    expect(component.value()).toBeNull();

    TestBed.inject(TranslocoService).setActiveLang("en");
    fixture.detectChanges();

    expect(component.value()).toBeNull();
  });
});

describe("ImmediateErrorStateMatcher", () => {
  // Tested in isolation, no Angular machinery needed — the class only
  // depends on a few plain function/object shapes.
  function fakeDateAdapter(parseResult: { isValid: boolean } | null) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return { parse: () => parseResult } as any;
  }

  function fakeFormField(errors: unknown[]) {
    return { errors: () => errors } as unknown as FormField<unknown>;
  }

  function fakeInputElement(value: string) {
    return signal({ nativeElement: { value } } as unknown as ElementRef<HTMLInputElement>);
  }

  it("reports a parse error for non-empty, unparsable text", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement("not a date"),
      fakeDateAdapter(null),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([]),
    );

    expect(matcher.isSignalErrorState(null)).toBe(true);
    expect(matcher.hasParseError()).toBe(true);
  });

  it("reports no parse error for empty text", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement(""),
      fakeDateAdapter(null),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([]),
    );

    expect(matcher.isSignalErrorState(null)).toBe(false);
    expect(matcher.hasParseError()).toBe(false);
  });

  it("reports no parse error for non-empty, successfully-parsed text", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement("1/1/2026"),
      fakeDateAdapter({ isValid: true }),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([]),
    );

    expect(matcher.isSignalErrorState(null)).toBe(false);
    expect(matcher.hasParseError()).toBe(false);
  });

  it("surfaces the parent form field's errors when the field is touched", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement(""),
      fakeDateAdapter(null),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([{ kind: "required", message: "Required" }]),
    );
    const touchedField = () => ({ touched: () => true }) as unknown as FieldState<unknown>;

    expect(matcher.isSignalErrorState(touchedField)).toBe(true);
    expect(matcher.hasParentError()).toBe(true);
  });

  it("ignores the parent form field's errors when the field is not touched", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement(""),
      fakeDateAdapter(null),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([{ kind: "required", message: "Required" }]),
    );
    const untouchedField = () => ({ touched: () => false }) as unknown as FieldState<unknown>;

    expect(matcher.isSignalErrorState(untouchedField)).toBe(false);
    expect(matcher.hasParentError()).toBe(false);
  });

  it("treats a null field (legacy isErrorState path) as touched by default", () => {
    const matcher = new ImmediateErrorStateMatcher(
      fakeInputElement(""),
      fakeDateAdapter(null),
      { parse: { dateInput: "D" } } as unknown as MatDateFormats,
      fakeFormField([{ kind: "required", message: "Required" }]),
    );

    expect(matcher.isErrorState(null, null)).toBe(true);
    expect(matcher.hasParentError()).toBe(true);
  });
});
