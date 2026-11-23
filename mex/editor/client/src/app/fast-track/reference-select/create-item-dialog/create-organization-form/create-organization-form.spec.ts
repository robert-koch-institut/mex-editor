import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { CreateOrganizationForm } from "./create-organization-form";

describe("CreateOrganizationForm", () => {
  let component: CreateOrganizationForm;
  let fixture: ComponentFixture<CreateOrganizationForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateOrganizationForm],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateOrganizationForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
