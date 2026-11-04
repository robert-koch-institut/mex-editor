import { Component, computed, HostBinding, input } from "@angular/core";
import { type FieldTree } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

import type { FieldCategory } from "../../shared/models";
import { ValidationErrorMessagePipe } from "../validation-error-label-pipe";

@Component({
  selector: "mex-fieldset",
  imports: [TranslocoPipe, ValidationErrorMessagePipe],
  templateUrl: "./fieldset.html",
  styleUrl: "./fieldset.scss",
})
/**
 * Component to wrap controls with label, description and errors.
 */
export class Fieldset<T> {
  private dataTestidSig = computed(() => {
    const state = this.formState();
    return state ? `fieldset-${state.name().split(".").at(-1)}` : null;
  });

  @HostBinding("attr.data-testid")
  get dataTestId() {
    return this.dataTestidSig();
  }

  labelKey = input.required<string>();
  labelParam = input<Record<string, unknown>>();
  descriptionKey = input<string>();

  showCategoryLabel = input(true);
  category = input.required<FieldCategory>();
  categoryKey = computed(() => `categories.${this.category()}`);

  showErrorWithoutTouch = input(false);

  formField = input<FieldTree<T>>();
  formState = computed(() => {
    const formField = this.formField();
    return formField ? formField() : null;
  });
}
