import { Component, computed, HostBinding, input } from "@angular/core";
import { type FieldTree } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";

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

  labelKey = input.required<string>();
  labelParam = input<Record<string, unknown>>();
  descriptionKey = input<string>();

  showCategoryLabel = input(true);
  category = input<"required" | "optional" | "recommended">("optional");
  categoryKey = computed(() => `categories.${this.category()}`);

  showErrorWithoutTouch = input(false);

  formField = input<FieldTree<T>>();
  formState = computed(() => {
    const formField = this.formField();
    return formField ? formField() : null;
  });
}
