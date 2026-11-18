import { Component } from "@angular/core";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import type { FieldTree } from "@angular/forms/signals";
import { By } from "@angular/platform-browser";
import type { TranslateParams } from "@jsverse/transloco";
import { TranslocoService } from "@jsverse/transloco";
import { vi } from "vitest";

import { Fieldset } from "./fieldset";

interface FakeErrorSpec {
  message: string;
  issue?: {
    path: (string | number)[];
  }; // defaults to the fake state's own keyInParent -> a "direct" (non-inner) error
}

function fakeFormField(state: {
  invalid?: boolean;
  touched?: boolean;
  errors?: FakeErrorSpec[];
  name?: string;
  keyInParent?: unknown;
  value?: unknown;
}) {
  const fieldState = {
    invalid: () => state.invalid ?? false,
    touched: () => state.touched ?? false,
    errors: () => state.errors ?? [],
    errorSummary: () =>
      (state.errors ?? []).map((e) => ({
        message: e.message,
        issue: e.issue,
        // fieldTree: () => ({ keyInParent: () => e.keyInParent ?? keyInParent }),
      })),
    name: () => state.name ?? "resourceForm.field",
    value: () => state.value,
  };
  return (() => fieldState) as unknown as FieldTree<unknown>;
}

// eslint-disable-next-line max-lines-per-function
describe("Fieldset", () => {
  let fixture: ComponentFixture<Fieldset<unknown>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [Fieldset] }).compileComponents();
    fixture = TestBed.createComponent(Fieldset);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function setInputs(inputs: {
    category: "required" | "optional" | "recommended"; // required input -- always supply it
    labelKey?: string;
    showCategoryLabel?: boolean;
    descriptionKey?: string;
    showErrorWithoutTouch?: boolean;
    formField?: FieldTree<unknown>;
  }) {
    for (const [key, value] of Object.entries(inputs)) {
      fixture.componentRef.setInput(key, value);
    }
  }

  it("shows only the label when showCategoryLabel is false", () => {
    setInputs({ labelKey: "title", category: "required", showCategoryLabel: false });
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

  it("renders the description when descriptionKey is set", () => {
    setInputs({ labelKey: "title", category: "optional", descriptionKey: "title.description" });
    fixture.detectChanges();

    const description = fixture.debugElement.query(By.css(".description"));
    expect(description.nativeElement.textContent.trim()).toBe("title.description");
  });

  it("renders no description block when descriptionKey is not set", () => {
    setInputs({ labelKey: "title", category: "optional" });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css(".description"))).toBeNull();
  });

  describe("data-testid", () => {
    it("is derived from the bound field's own name (last path segment)", () => {
      setInputs({
        labelKey: "title",
        category: "optional",
        formField: fakeFormField({ name: "resourceForm.title" }),
      });
      fixture.detectChanges();

      expect(fixture.nativeElement.getAttribute("data-testid")).toBe("fieldset-title");
    });

    it("has no data-testid when no formField is bound", () => {
      setInputs({ labelKey: "title", category: "optional" });
      fixture.detectChanges();

      expect(fixture.nativeElement.getAttribute("data-testid")).toBeNull();
    });
  });

  describe("errors", () => {
    it("shows errors when invalid and touched", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        formField: fakeFormField({
          invalid: true,
          touched: true,
          errors: [{ message: "validation.required" }],
        }),
      });
      fixture.detectChanges();

      const errorText = fixture.debugElement.query(By.css(".error-container")).nativeElement
        .textContent;
      expect(errorText).toContain("validation.required");
    });

    it("renders one .error block per errorSummary() entry", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        formField: fakeFormField({
          invalid: true,
          touched: true,
          errors: [{ message: "validation.required" }, { message: "validation.tooShort" }],
        }),
      });
      fixture.detectChanges();

      expect(fixture.debugElement.queryAll(By.css(".error")).length).toBe(2);
    });

    it("hides errors when invalid but untouched, by default (showErrorWithoutTouch=false)", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        formField: fakeFormField({
          invalid: true,
          touched: false,
          errors: [{ message: "validation.required" }],
        }),
      });
      fixture.detectChanges();

      expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
    });

    it("shows errors when invalid and untouched, if showErrorWithoutTouch is true", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        showErrorWithoutTouch: true,
        formField: fakeFormField({
          invalid: true,
          touched: false,
          errors: [{ message: "validation.required" }],
        }),
      });
      fixture.detectChanges();

      expect(fixture.debugElement.query(By.css(".error-container"))).not.toBeNull();
    });

    it("hides errors when the field is valid, even if touched", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        formField: fakeFormField({
          invalid: false,
          touched: true,
          errors: [{ message: "validation.required", issue: { path: ["title"] } }],
        }),
      });
      fixture.detectChanges();

      expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
    });

    it("does not show an error container when no formField is provided at all", () => {
      setInputs({ labelKey: "title", category: "required" });
      fixture.detectChanges();

      expect(fixture.debugElement.query(By.css(".error-container"))).toBeNull();
    });

    it("passes the field label through as-is for a direct (non-inner) error", () => {
      setInputs({
        labelKey: "title",
        category: "required",
        formField: fakeFormField({
          invalid: true,
          touched: true,
          keyInParent: "title",
          errors: [{ message: "validation.required", issue: { path: ["title"] } }], // same key -> not "inner"
        }),
      });
      fixture.detectChanges();

      const errorText = fixture.debugElement.query(By.css(".error")).nativeElement.textContent;
      expect(errorText).toContain("validation.required");
    });
  });
});

describe("Fieldset content projection", () => {
  @Component({
    standalone: true,
    imports: [Fieldset],
    template: `<mex-fieldset labelKey="title" category="optional"
      ><button>projected content</button></mex-fieldset
    >`,
  })
  class Host {}

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("projects content passed between the component tags", async () => {
    await TestBed.configureTestingModule({ imports: [Host] }).compileComponents();

    const translocoService = TestBed.inject(TranslocoService);
    vi.spyOn(translocoService, "translate").mockImplementation((key: TranslateParams) => key);

    const hostFixture = TestBed.createComponent(Host);
    hostFixture.detectChanges();

    expect(hostFixture.nativeElement.textContent).toContain("projected content");
  });
});
