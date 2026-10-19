import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import type { FieldTree } from "@angular/forms/signals";
import { provideLuxonDateAdapter } from "@angular/material-luxon-adapter";
import { By } from "@angular/platform-browser";
import { TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";
import { vi } from "vitest";

import { Datepicker } from "./datepicker";

function fakeFieldTree(state: { errors?: unknown[]; touched?: boolean } = {}) {
  const fieldState = {
    errors: () => state.errors ?? [],
    touched: () => state.touched ?? false,
  };
  return (() => fieldState) as unknown as FieldTree<unknown>;
}

function setNativeValue(
  fixture: ComponentFixture<unknown>,
  input: HTMLInputElement,
  value: string,
) {
  input.value = value;
  input.dispatchEvent(new Event("input"));
  input.dispatchEvent(new Event("blur"));
  fixture.detectChanges();
}

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

    // Required host-directive input -- must be set before the first
    // detectChanges(), see the file-level comment above.
    fixture.componentRef.setInput("formField", fakeFieldTree());

    fixture.detectChanges();
  });

  it("creates with a null value by default", () => {
    expect(component.value()).toBeNull();
  });

  it("parses a typed date into the value", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "01.01.2026");

    expect(component.value()?.isValid).toBe(true);
    expect(component.value()?.toISODate()).toBe("2026-01-01");
  });

  it("flags a parse error and shows the hint for unparsable text", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "not a date");

    expect(component.hasParseError()).toBe(true);
    expect(fixture.debugElement.query(By.css(".error-hint"))).not.toBeNull();
  });

  it("does not flag a parse error when the input is empty", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "");

    expect(component.hasParseError()).toBe(false);
    expect(fixture.debugElement.query(By.css(".error-hint"))).toBeNull();
  });

  it("clears the parse error once a previously-invalid value becomes valid", () => {
    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    setNativeValue(fixture, input, "not a date");
    fixture.detectChanges();
    expect(component.hasParseError()).toBe(true);

    setNativeValue(fixture, input, "01.01.2026");
    fixture.detectChanges();

    expect(component.hasParseError()).toBe(false);
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

  it("reflects minDate/maxDate inputs (shallow check -- binding only, not enforced-range behavior)", () => {
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
