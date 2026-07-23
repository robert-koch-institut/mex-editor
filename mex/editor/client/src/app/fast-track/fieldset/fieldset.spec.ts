import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { Fieldset } from "./fieldset";
import { inputBinding } from "@angular/core";

describe("Fieldset", () => {
  let component: Fieldset<unknown>;
  let fixture: ComponentFixture<Fieldset<unknown>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Fieldset],
    }).compileComponents();

    fixture = TestBed.createComponent(Fieldset, {
      bindings: [inputBinding("labelKey", () => "test.fieldset.label")],
    });
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
