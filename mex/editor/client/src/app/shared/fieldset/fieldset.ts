import { Component, computed, HostBinding, input } from "@angular/core";
import { type Field } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

import { FieldErrors } from "../field-errors/field-errors";
import { readFieldMetadata } from "../field-metadata.pipe";
import type { FieldCategory } from "../models";

@Component({
  selector: "mex-fieldset",
  imports: [FieldErrors, TranslocoPipe],
  templateUrl: "./fieldset.html",
  styleUrl: "./fieldset.scss",
})
/**
 * Component to wrap controls with label, description and errors.
 */
export class Fieldset<T> {
  formField = input<Field<T>>();

  labelKey = input<string>("");
  labelParam = input<Record<string, unknown>>();
  protected readonly fieldLabelKey = computed(() => {
    const field = this.formField();
    return field && readFieldMetadata(field, "labelKey");
  });

  descriptionKey = input<string>();
  protected readonly fieldDescriptionKey = computed(() => {
    const field = this.formField();
    return field && readFieldMetadata(field, "descriptionKey");
  });

  showErrors = input(true);
  showErrorsWithoutTouch = input(false);
  showDescription = input(true);
  showCategoryLabel = input(true);
  category = input.required<FieldCategory>();
  categoryKey = computed(() => `categories.${this.category()}`);

  @HostBinding("attr.data-testid")
  get dataTestId() {
    return this.dataTestidSig();
  }

  private readonly fieldState = computed(() => {
    return this.formField()?.();
  });

  private readonly dataTestidSig = computed(() => {
    const state = this.fieldState();
    return state ? `fieldset-${state.name().split(".").at(-1)}` : null;
  });
}
