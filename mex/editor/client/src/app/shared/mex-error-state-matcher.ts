import type { AbstractControl, FormGroupDirective, NgForm } from "@angular/forms";
import type { Field } from "@angular/forms/signals";
import { ErrorStateMatcher } from "@angular/material/core";

/**
 * MEx specfic ErrorStateMatcher.
 */
export class MexErrorStateMatcher extends ErrorStateMatcher {
  override isErrorState(
    control: AbstractControl | null,
    f: FormGroupDirective | NgForm | null,
  ): boolean {
    const result = super.isErrorState(control, f);
    console.log("MyErrorMatcher :: isErrorState", control, f, result);
    return result;
  }
  override isSignalErrorState(field: Field<unknown> | null): boolean {
    if (!super.isSignalErrorState) {
      throw new Error("WTF");
    }
    const result = super.isSignalErrorState(field);
    console.log("MyErrorMatcher :: isSignalErrorState", field, result);
    return result;
  }
}
