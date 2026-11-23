import { Component, input } from "@angular/core";
import type { Field } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

import { FieldError } from "../field-error/field-error";
import { FieldMetadataPipe } from "../field-metadata.pipe";

@Component({
  imports: [FieldError, FieldMetadataPipe, TranslocoPipe],
  selector: "mex-field-errors",
  styleUrl: "./field-errors.scss",
  templateUrl: "./field-errors.html",
})
/**
 * Component to show all errors of a field.
 */
export class FieldErrors<T> {
  formField = input.required<Field<T>>();
  fieldLabel = input<string>();

  showErrorsWithoutTouch = input(false);
}
