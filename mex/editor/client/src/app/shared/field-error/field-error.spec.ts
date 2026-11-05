import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FieldError } from "./field-error";

describe("Error", () => {
  let component: FieldError;
  let fixture: ComponentFixture<FieldError>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FieldError],
    }).compileComponents();

    fixture = TestBed.createComponent(FieldError);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
