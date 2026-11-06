import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ErrorSummary } from "./error-summary";

describe("ErrorSummary", () => {
  let component: ErrorSummary;
  let fixture: ComponentFixture<ErrorSummary>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ErrorSummary],
    }).compileComponents();

    fixture = TestBed.createComponent(ErrorSummary);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
