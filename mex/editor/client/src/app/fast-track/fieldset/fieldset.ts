import type { PipeTransform } from "@angular/core";
import { Component, computed, HostBinding, inject, input, Pipe } from "@angular/core";
import type { FieldState, ValidationError } from "@angular/forms/signals";
import { type FieldTree } from "@angular/forms/signals";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";

import type { FieldCategory } from "../../shared/models";

@Pipe({
  name: "fieldErrorLabel",
})
/**
 * Transforms field errors to human readable text.
 */
class FieldErrorLabel implements PipeTransform {
  private transloco = inject(TranslocoService);
  transform(
    value: ValidationError.WithFieldTree,
    state: FieldState<unknown>,
    originalLabel: string,
  ) {
    const errorKey = value.fieldTree().keyInParent();
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

@Component({
  selector: "mex-fieldset",
  imports: [FieldErrorLabel, TranslocoPipe],
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
