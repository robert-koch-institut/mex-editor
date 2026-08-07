import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { CreateContactPointForm } from "./create-contact-point-form";

describe("CreateContactPointForm", () => {
  let component: CreateContactPointForm;
  let fixture: ComponentFixture<CreateContactPointForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateContactPointForm],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateContactPointForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
