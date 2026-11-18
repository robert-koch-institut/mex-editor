import { Component, computed, input } from "@angular/core";
import { translateSignal, TranslocoPipe } from "@jsverse/transloco";

import { FieldErrorSummary } from "../field-error-summary/field-error-summary";
import type { FieldCategory } from "../models";

@Component({
  selector: "mex-fieldset",
  imports: [FieldErrorSummary, TranslocoPipe],
  templateUrl: "./fieldset.html",
  styleUrl: "./fieldset.scss",
})
/**
 * Component to wrap controls with label, description and errors.
 */
export class Fieldset {
  labelKey = input.required<string>();
  labelParam = input<Record<string, unknown>>();
  label = translateSignal(this.labelKey, this.labelParam);
  descriptionKey = input<string>();

  showCategoryLabel = input(true);
  category = input.required<FieldCategory>();
  categoryKey = computed(() => `categories.${this.category()}`);
}
