import { Component, input } from "@angular/core";
import type { ValidationError } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

import { ValidationErrorMessagePipe } from "../../fast-track/validation-error-message-pipe";

@Component({
  selector: "mex-field-error",
  imports: [TranslocoPipe, ValidationErrorMessagePipe],
  templateUrl: "./field-error.html",
  styleUrl: "./field-error.scss",
})
/**
 * Component to display validation erros in mex.
 */
export class FieldError {
  error = input.required<ValidationError.WithFieldTree>();
  fieldLabel = input.required<string>();
}
