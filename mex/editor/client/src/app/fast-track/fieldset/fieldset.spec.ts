import { Component } from "@angular/core";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import type { FieldTree } from "@angular/forms/signals";
import { By } from "@angular/platform-browser";
import { TranslocoService } from "@jsverse/transloco";

import { Fieldset } from "./fieldset";

/**
 * Builds a minimal fake FieldTree: `formField` is itself a callable that
 * returns a FieldState-like object exposing `.errors()` / `.touched()`
 * signals, matching what `fieldset.html` reads (`state.errors()`,
 * `state.touched()`, `err.kind`, `err.message`).
 */
function fakeFormField(state: { errors?: { kind: string; message: string }[]; touched?: boolean }) {
  const fieldState = {
    name: () => "",
    errors: () => state.errors ?? [],
    touched: () => state.touched ?? false,
  };
  return (() => fieldState) as unknown as FieldTree<unknown>;
}

// eslint-disable-next-line max-lines-per-function
describe("Fieldset", () => {
  let fixture: ComponentFixture<Fieldset<unknown>>;

  beforeEach(async () => {
    // Relies on the project's own (globally provided) TranslocoService —
    // no override/import here — and only replaces `translate()` with an
    // identity stub, so label()/categoryLabel()/description() just echo
    // the key back and assertions don't depend on real translation files.
    await TestBed.configureTestingModule({
      imports: [Fieldset],
    }).compileComponents();

    const translocoService = TestBed.inject(TranslocoService);
    vi.spyOn(translocoService, "translate").mockImplementation((key: string | string[]) =>
      typeof key === "string" ? key : key[0],
    );

    fixture = TestBed.createComponent(Fieldset);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function setInputs(
    inputs: Partial<{
      labelKey: string;
      showCategoryLabel: boolean;
      category: "required" | "optional" | "recommended";
      descriptionKey: string;
      formField: FieldTree<unknown>;
    }>,
  ) {
    for (const [key, value] of Object.entries(inputs)) {
      fixture.componentRef.setInput(key, value);
    }
  }

  it("shows only the label when showCategoryLabel is false", () => {
    setInputs({ labelKey: "title", showCategoryLabel: false });
    fixture.detectChanges();

    const labelText = fixture.debugElement.query(By.css(".label")).nativeElement.textContent.trim();
    expect(labelText).toBe("title");
  });

  it("shows the label combined with the category label by default", () => {
    setInputs({ labelKey: "title", category: "required" });
    fixture.detectChanges();

    const labelText = fixture.debugElement
      .query(By.css(".label"))
      .nativeElement.textContent.replace(/\s+/g, " ")
      .trim();
    expect(labelText).toBe("title - categories.required");
  });

  it("shows the 'recommended' category label when set", () => {
    setInputs({ labelKey: "title", category: "recommended" });
    fixture.detectChanges();

    const labelText = fixture.debugElement
      .query(By.css(".label"))
      .nativeElement.textContent.replace(/\s+/g, " ")
      .trim();
    expect(labelText).toBe("title - categories.recommended");
  });

  it("defaults to the 'optional' category when none is provided", () => {
    setInputs({ labelKey: "title" });
    fixture.detectChanges();

    const labelText = fixture.debugElement
      .query(By.css(".label"))
      .nativeElement.textContent.replace(/\s+/g, " ")
      .trim();
    expect(labelText).toBe("title - categories.optional");
  });

  it("renders the description when descriptionKey is set", () => {
    setInputs({ labelKey: "title", descriptionKey: "title.description" });
    fixture.detectChanges();

    const description = fixture.debugElement.query(By.css(".description"));
    expect(description.nativeElement.textContent.trim()).toBe("title.description");
  });

  it("renders no description block when descriptionKey is not set", () => {
    setInputs({ labelKey: "title" });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css(".description"))).toBeNull();
  });

  it("shows errors when the field is touched and has errors", () => {
    setInputs({
      labelKey: "title",
      formField: fakeFormField({
        touched: true,
        errors: [{ kind: "required", message: "Title is required" }],
      }),
    });
    fixture.detectChanges();

    const errorText = fixture.debugElement.query(By.css(".error-container")).nativeElement
      .textContent;
    expect(errorText).toContain("required");
    expect(errorText).toContain("Title is required");
  });

  it("renders one .error block per error", () => {
    setInputs({
      labelKey: "title",
      formField: fakeFormField({
        touched: true,
        errors: [
          { kind: "required", message: "Title is required" },
          { kind: "minLength", message: "Too short" },
        ],
      }),
    });
    fixture.detectChanges();

    const errorNodes = fixture.debugElement.queryAll(By.css(".error"));
    expect(errorNodes.length).toBe(2);
  });

  it("does not show errors when the field has errors but is not touched", () => {
    setInputs({
      labelKey: "title",
      formField: fakeFormField({
        touched: false,
        errors: [{ kind: "required", message: "Title is required" }],
      }),
    });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
  });

  it("does not show errors when the field is touched but has no errors", () => {
    setInputs({
      labelKey: "title",
      formField: fakeFormField({ touched: true, errors: [] }),
    });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
  });

  it("does not show an error container when no formField is provided at all", () => {
    setInputs({ labelKey: "title" });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
  });
});

describe("Fieldset content projection", () => {
  // Separate TestBed setup: a projection test needs its own host component,
  // and TestBed can't be reconfigured after a component has already been
  // created in another describe block's beforeEach.
  @Component({
    standalone: true,
    imports: [Fieldset],
    template: `<mex-fieldset labelKey="title"><button>projected content</button></mex-fieldset>`,
  })
  class Host {}

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("projects content passed between the component tags", async () => {
    await TestBed.configureTestingModule({
      imports: [Host],
    }).compileComponents();
    const hostFixture = TestBed.createComponent(Host);
    hostFixture.detectChanges();

    expect(hostFixture.nativeElement.textContent).toContain("projected content");
  });
});
