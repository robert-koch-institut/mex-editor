import { Component, computed, input } from "@angular/core";
import type { ValidationError } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

import { readFieldMetadata } from "../field-metadata.pipe";
import { ValidationErrorMessagePipe } from "../validation-error-message-pipe";

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
  fieldLabel = input<string>();

  protected readonly innerFieldLabel = computed(() => {
    return this.fieldLabel() ?? `{{${readFieldMetadata(this.error().fieldTree, "labelKey")}}}`;
  });
}
