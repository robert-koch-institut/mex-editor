import { Component, input } from "@angular/core";
import type { Field } from "@angular/forms/signals";

import { FieldError } from "../field-error/field-error";
import { FieldMetadataPipe } from "../field-metadata.pipe";

@Component({
  imports: [FieldError, FieldMetadataPipe],
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

  // protected readonly inputLabel = translateSignal(this.labelKey, this.labelParam);
  // label = computed(() => {
  //   const field = this.formField();
  //   const metadataLabel = field && readFieldMetadata(field, "label");
  //   return metadataLabel ?? this.inputLabel();
  // });
}
