import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { CreatePersonForm } from "./create-person-form";
import { By } from "@angular/platform-browser";

function setNativeValue(
  fixture: ComponentFixture<unknown>,
  input: HTMLInputElement,
  value: string,
) {
  input.value = value;
  input.dispatchEvent(new Event("input"));
  input.dispatchEvent(new Event("change"));
  fixture.detectChanges();
}

describe("CreatePersonForm", () => {
  let fixture: ComponentFixture<CreatePersonForm>;
  let component: CreatePersonForm;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [CreatePersonForm] }).compileComponents();
    fixture = TestBed.createComponent(CreatePersonForm);
    component = fixture.componentInstance;
  });

  it("splits inputText into givenName/familyName as the initial data", () => {
    fixture.componentRef.setInput("inputText", "Jane Doe");
    fixture.detectChanges();

    expect(component.data()).toEqual({
      $type: "CreatePerson",
      givenName: "Jane",
      familyName: "Doe",
    });
  });

  it("puts any extra words into familyName", () => {
    fixture.componentRef.setInput("inputText", "Jane van Doe");
    fixture.detectChanges();

    expect(component.data()).toEqual({
      $type: "CreatePerson",
      givenName: "Jane",
      familyName: "van Doe",
    });
  });

  it("starts with empty names and is invalid when there's no inputText", () => {
    fixture.detectChanges();

    expect(component.data()).toEqual({ $type: "CreatePerson", givenName: "", familyName: "" });
    expect(component.isValid()).toBe(false);
  });

  it("seeds the form from an initial `data` input instead of inputText, when given", () => {
    fixture.componentRef.setInput("data", {
      $type: "CreatePerson",
      givenName: "Preset",
      familyName: "Name",
    });
    fixture.detectChanges();

    const [givenNameInput, familyNameInput] = fixture.debugElement.queryAll(By.css("input"));
    expect((givenNameInput.nativeElement as HTMLInputElement).value).toBe("Preset");
    expect((familyNameInput.nativeElement as HTMLInputElement).value).toBe("Name");
  });

  it("is invalid while familyName is empty even if givenName is filled", () => {
    fixture.detectChanges();
    const [givenNameInput] = fixture.debugElement.queryAll(By.css("input"));
    setNativeValue(fixture, givenNameInput.nativeElement, "Jane");

    expect(component.isValid()).toBe(false);
  });

  it("is invalid while givenName is empty even if familyName is filled", () => {
    fixture.detectChanges();
    const [, familyNameInput] = fixture.debugElement.queryAll(By.css("input"));
    setNativeValue(fixture, familyNameInput.nativeElement, "Doe");

    expect(component.isValid()).toBe(false);
  });

  it("becomes valid once both givenName and familyName are filled, and reports the data", () => {
    fixture.detectChanges();
    const [givenNameInput, familyNameInput] = fixture.debugElement.queryAll(By.css("input"));
    setNativeValue(fixture, givenNameInput.nativeElement, "Jane");
    setNativeValue(fixture, familyNameInput.nativeElement, "Doe");

    expect(component.isValid()).toBe(true);
    expect(component.data()).toEqual({
      $type: "CreatePerson",
      givenName: "Jane",
      familyName: "Doe",
    });
  });
});
