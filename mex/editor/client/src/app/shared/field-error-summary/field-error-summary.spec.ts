import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FieldErrorSummary } from "./field-error-summary";

describe("ErrorSummary", () => {
  let component: FieldErrorSummary;
  let fixture: ComponentFixture<FieldErrorSummary>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FieldErrorSummary],
    }).compileComponents();

    fixture = TestBed.createComponent(FieldErrorSummary);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
