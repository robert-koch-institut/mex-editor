import { Component, input } from "@angular/core";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import type { FieldState } from "@angular/forms/signals";

import { FieldError } from "../field-error/field-error";
import { FieldErrorSummary } from "./field-error-summary";

/** Replaces FieldError so only the summary logic is tested. */
@Component({ selector: "mex-field-error", template: `{{ error().kind }}` })
class StubFieldError {
  readonly error = input.required<{ kind: string }>();
  readonly fieldLabel = input.required<string>();
}

function stateWith(opts: {
  invalid: boolean;
  touched: boolean;
  errors?: { kind: string }[];
  summary?: { kind: string }[];
}): FieldState<unknown> {
  return {
    invalid: () => opts.invalid,
    touched: () => opts.touched,
    errors: () => opts.errors ?? [],
    errorSummary: () => opts.summary ?? [],
  } as unknown as FieldState<unknown>;
}

describe("FieldErrorSummary", () => {
  let fixture: ComponentFixture<FieldErrorSummary>;

  beforeEach(async () => {
    TestBed.overrideComponent(FieldErrorSummary, {
      remove: { imports: [FieldError] },
      add: { imports: [StubFieldError] },
    });
    await TestBed.configureTestingModule({ imports: [FieldErrorSummary] }).compileComponents();
    fixture = TestBed.createComponent(FieldErrorSummary);
    fixture.componentRef.setInput("fieldLabel", "Name");
  });

  const render = async (state: FieldState<unknown>, inputs: Record<string, boolean> = {}) => {
    fixture.componentRef.setInput("fieldState", state);
    for (const [k, v] of Object.entries(inputs)) fixture.componentRef.setInput(k, v);
    await fixture.whenStable();
    return Array.from(
      (fixture.nativeElement as HTMLElement).querySelectorAll("mex-field-error"),
    ).map((e) => e.textContent?.trim());
  };

  it("shows nothing for a valid field", async () => {
    expect(await render(stateWith({ invalid: false, touched: true }))).toEqual([]);
  });

  it("hides errors of an untouched field", async () => {
    const state = stateWith({ invalid: true, touched: false, errors: [{ kind: "required" }] });
    expect(await render(state)).toEqual([]);
  });

  it("shows errors of a touched field", async () => {
    const state = stateWith({ invalid: true, touched: true, errors: [{ kind: "required" }] });
    expect(await render(state)).toEqual(["required"]);
  });

  it("shows errors of an untouched field with showErrorsWithoutTouch", async () => {
    const state = stateWith({ invalid: true, touched: false, errors: [{ kind: "required" }] });
    expect(await render(state, { showErrorsWithoutTouch: true })).toEqual(["required"]);
  });

  it("uses the nested error summary only with showNestedErrors", async () => {
    const state = stateWith({
      invalid: true,
      touched: true,
      errors: [{ kind: "own" }],
      summary: [{ kind: "own" }, { kind: "nested" }],
    });
    expect(await render(state)).toEqual(["own"]);
    expect(await render(state, { showNestedErrors: true })).toEqual(["own", "nested"]);
  });
});
