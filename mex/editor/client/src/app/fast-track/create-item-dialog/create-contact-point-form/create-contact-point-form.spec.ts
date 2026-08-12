import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { By } from "@angular/platform-browser";

import { CreateContactPointForm } from "./create-contact-point-form";

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

describe("CreateContactPointForm", () => {
  let fixture: ComponentFixture<CreateContactPointForm>;
  let component: CreateContactPointForm;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [CreateContactPointForm] }).compileComponents();
    fixture = TestBed.createComponent(CreateContactPointForm);
    component = fixture.componentInstance;
  });

  it("seeds email from inputText as the initial data", () => {
    fixture.componentRef.setInput("inputText", "jane.doe@example.org");
    fixture.detectChanges();

    expect(component.data()).toEqual({
      $type: "CreateContactPoint",
      email: "jane.doe@example.org",
    });
  });

  it("starts empty and invalid when there's no inputText", () => {
    fixture.detectChanges();

    expect(component.data()).toEqual({ $type: "CreateContactPoint", email: "" });
    expect(component.isValid()).toBe(false);
  });

  it("seeds the form from an initial `data` input instead of inputText, when given", () => {
    fixture.componentRef.setInput("data", {
      $type: "CreateContactPoint",
      email: "preset@example.org",
    });
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css("input")).nativeElement as HTMLInputElement;
    expect(input.value).toBe("preset@example.org");
  });

  it("is invalid for a malformed email address", () => {
    fixture.detectChanges();
    const input = fixture.debugElement.query(By.css("input")).nativeElement;
    setNativeValue(fixture, input, "not-an-email");

    expect(component.isValid()).toBe(false);
  });

  it("is invalid for an empty email address", () => {
    fixture.componentRef.setInput("inputText", "jane.doe@example.org");
    fixture.detectChanges();
    const input = fixture.debugElement.query(By.css("input")).nativeElement;
    setNativeValue(fixture, input, "");

    expect(component.isValid()).toBe(false);
  });

  it("becomes valid once a well-formed email is entered, and reports the data", () => {
    fixture.detectChanges();
    const input = fixture.debugElement.query(By.css("input")).nativeElement;
    setNativeValue(fixture, input, "jane.doe@example.org");

    expect(component.isValid()).toBe(true);
    expect(component.data()).toEqual({
      $type: "CreateContactPoint",
      email: "jane.doe@example.org",
    });
  });
});
