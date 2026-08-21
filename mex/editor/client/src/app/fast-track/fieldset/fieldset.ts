import { Component, computed, HostBinding, inject, input } from "@angular/core";
import type { FieldState, ValidationError } from "@angular/forms/signals";
import { type FieldTree } from "@angular/forms/signals";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";

import type { FieldCategory } from "../../shared/models";

@Component({
  selector: "mex-fieldset",
  imports: [TranslocoPipe],
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

  private transloco = inject(TranslocoService);
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

  getErrorFieldLabel(
    state: FieldState<unknown>,
    error: ValidationError.WithFieldTree,
    originalLabel: string,
  ) {
    const errorKey = error.fieldTree().keyInParent();
    const isInnerError = errorKey !== state.keyInParent();
    if (isInnerError) {
      if (state.value() instanceof Array) {
        return this.transloco.translate("validation.innerArrayError", {
          field: originalLabel,
          position: (typeof errorKey == "string" ? parseInt(errorKey) : errorKey) + 1,
        });
      }
      return this.transloco.translate("validation.innerObjectError", {
        field: originalLabel,
        property: errorKey,
      });
    }

    return originalLabel;
  }
}
