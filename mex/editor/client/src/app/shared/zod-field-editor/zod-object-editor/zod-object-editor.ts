import { Component, computed, forwardRef, input, model, output } from "@angular/core";
import type { FormValueControl } from "@angular/forms/signals";
import { disabled, form, readonly, validateStandardSchema } from "@angular/forms/signals";
import { TranslocoPipe } from "@jsverse/transloco";
import type z from "zod";
import type { ZodObject } from "zod";

import { FieldCategoryPipe } from "../../field-category-pipe";
import { FieldError } from "../../field-error/field-error";
import { FieldErrorSummary } from "../../field-error-summary/field-error-summary";
import { Fieldset } from "../../fieldset/fieldset";
import { ZodFieldEditor } from "../zod-field-editor";

@Component({
  imports: [
    FieldCategoryPipe,
    FieldError,
    FieldErrorSummary,
    Fieldset,
    forwardRef(() => ZodFieldEditor),
    TranslocoPipe,
  ],
  selector: "mex-zod-object-editor",
  styleUrl: "./zod-object-editor.scss",
  templateUrl: "./zod-object-editor.html",
})
/**
 * Docs
 */
export class ZodObjectEditor<T extends ZodObject> implements FormValueControl<z.infer<T>> {
  readonly schema = input.required<T>();
  readonly value = model.required<z.infer<T>>();

  readonly disabled = input(false);
  readonly readonly = input(false);

  readonly touch = output<void>();

  readonly innerForm = form<Record<string, unknown>>(this.value, (path) => {
    validateStandardSchema(path, () => this.schema());
    disabled(path, { when: () => this.disabled() });
    readonly(path, { when: () => this.readonly() });
  });

  readonly entries = computed(() => {
    const shape = this.schema().shape;
    return Object.entries(shape).map(([key, schema]) => ({
      key,
      schema,
    }));
  });
}
