import { Component, computed, inject, input } from "@angular/core";
import type { FieldTree } from "@angular/forms/signals";
import { TranslocoService } from "@jsverse/transloco";

@Component({
  selector: "mex-fieldset",
  imports: [],
  templateUrl: "./fieldset.html",
  styleUrl: "./fieldset.scss",
})
/**
 * Component to wrap controls with label, description and errors.
 */
export class Fieldset<T> {
  private _transloco = inject(TranslocoService);

  labelKey = input.required<string>();
  label = computed(() => this._transloco.translate(this.labelKey()));

  showCategoryLabel = input(true);
  category = input<"required" | "optional" | "desired">("optional");
  categoryLabel = computed(() => this._transloco.translate(`categories.${this.category()}`));

  formField = input<FieldTree<T>>();
  formState = computed(() => {
    const formField = this.formField();
    return formField ? formField() : null;
  });

  descriptionKey = input<string>();
  description = computed(() => {
    const key = this.descriptionKey();
    return key ? this._transloco.translate(key) : undefined;
  });
}
