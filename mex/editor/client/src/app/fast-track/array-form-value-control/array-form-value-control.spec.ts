import { ComponentFixture, TestBed } from "@angular/core/testing";

import { ArrayFormValueControl } from "./array-form-value-control";

describe("ArrayFormValueControl", () => {
  let component: ArrayFormValueControl;
  let fixture: ComponentFixture<ArrayFormValueControl>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArrayFormValueControl],
    }).compileComponents();

    fixture = TestBed.createComponent(ArrayFormValueControl);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
