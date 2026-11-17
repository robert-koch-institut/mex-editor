import { Component, computed, input } from "@angular/core";
import { TranslocoPipe } from "@jsverse/transloco";

import { FieldErrorSummary } from "../../shared/field-error-summary/field-error-summary";
import type { FieldCategory } from "../../shared/models";

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
  // private dataTestidSig = computed(() => {
  //   const state = this.formState();
  //   return state ? `fieldset-${state.name().split(".").at(-1)}` : null;
  // });

  // @HostBinding("attr.data-testid")
  // get dataTestId() {
  //   return this.dataTestidSig();
  // }

  labelKey = input.required<string>();
  labelParam = input<Record<string, unknown>>();
  descriptionKey = input<string>();

  showCategoryLabel = input(true);
  category = input.required<FieldCategory>();
  categoryKey = computed(() => `categories.${this.category()}`);

  // showErrorWithoutTouch = input(false);

  // formField = input<FieldTree<T>>();
  // formState = computed(() => {
  //   const formField = this.formField();
  //   return formField ? formField() : null;
  // });
}
