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
    return super.isErrorState(control, f);
  }
  override isSignalErrorState(field: Field<unknown> | null): boolean {
    if (!super.isSignalErrorState) {
      return false;
    }
    return super.isSignalErrorState(field);
  }
}
