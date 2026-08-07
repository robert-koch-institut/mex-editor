import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ReferenceSelect } from "./reference-select";

describe("ReferenceSelect", () => {
  let component: ReferenceSelect;
  let fixture: ComponentFixture<ReferenceSelect>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReferenceSelect],
    }).compileComponents();

    fixture = TestBed.createComponent(ReferenceSelect);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
