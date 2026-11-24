import { Component, input } from "@angular/core";
import type { FieldState } from "@angular/forms/signals";

import { FieldError } from "../field-error/field-error";

@Component({
  selector: "mex-field-error-summary",
  imports: [FieldError],
  templateUrl: "./field-error-summary.html",
  styleUrl: "./field-error-summary.scss",
})
/**
 * Component to display a error summary in mex.
 */
export class FieldErrorSummary {
  fieldState = input.required<FieldState<unknown>>();
  fieldLabel = input.required<string>();

  showErrorsWithoutTouch = input(false);
  showNestedErrors = input(false);
}
