import { Pipe, type PipeTransform } from "@angular/core";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import type { ValidationError } from "@angular/forms/signals";
import { TranslocoService, TranslocoTestingModule } from "@jsverse/transloco";

import { ValidationErrorMessagePipe } from "../validation-error-message-pipe";
import { FieldError } from "./field-error";

/** Isolates FieldError from the real mapping of validation errors to message keys. */
@Pipe({ name: "validationErrorMessage" })
class StubValidationErrorMessagePipe implements PipeTransform {
  transform() {
    return { msgKey: "test.key", params: { min: 3 } };
  }
}

describe("FieldError", () => {
  let fixture: ComponentFixture<FieldError>;

  beforeEach(async () => {
    TestBed.overrideComponent(FieldError, {
      remove: { imports: [ValidationErrorMessagePipe] },
      add: { imports: [StubValidationErrorMessagePipe] },
    });
    await TestBed.configureTestingModule({
      imports: [
        FieldError,
        TranslocoTestingModule.forRoot({
          // eslint-disable-next-line @typescript-eslint/naming-convention
          langs: { en: { "test.key": "{{field}} needs {{min}}" } },
          translocoConfig: { availableLangs: ["en"], defaultLang: "en" },
        }),
      ],
    }).compileComponents();
    vitest.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("en");

    fixture = TestBed.createComponent(FieldError);
    fixture.componentRef.setInput("error", { kind: "minLength" } as ValidationError.WithFieldTree);
    fixture.componentRef.setInput("fieldLabel", "Name");
    await fixture.whenStable();
  });

  it("translates the message key with the error params and the field label", () => {
    expect(fixture.nativeElement.querySelector(".error").textContent.trim()).toBe("Name needs 3");
  });
});
