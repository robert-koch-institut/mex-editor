import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { Datepicker } from "./datepicker";

describe("Datepicker", () => {
  let component: Datepicker;
  let fixture: ComponentFixture<Datepicker>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Datepicker],
    }).compileComponents();

    fixture = TestBed.createComponent(Datepicker);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
