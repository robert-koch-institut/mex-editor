import type { WritableSignal } from "@angular/core";
import { Component, computed, forwardRef, input, model, output } from "@angular/core";
import type { FieldTree, FormValueControl } from "@angular/forms/signals";
import { disabled, form, readonly, validateStandardSchema } from "@angular/forms/signals";
import type z from "zod";

import { Fieldset } from "../../fast-track/fieldset/fieldset";
import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import { ZodFieldEditor } from "../zod-field-editor/zod-field-editor";

function objectEntries(schema: z.ZodType): { key: string; schema: z.ZodType }[] {
  const shape = (schema as z.ZodObject).shape as Record<string, z.ZodType>;
  return Object.entries(shape).map(([key, child]) => ({ key, schema: child }));
}

@Component({
  imports: [FieldCategoryPipe, Fieldset, forwardRef(() => ZodFieldEditor)],
  selector: "mex-zod-object-editor",
  styleUrl: "./zod-object-editor.scss",
  templateUrl: "./zod-object-editor.html",
})
/**
 * Docs
 */
export class ZodObjectEditor<S extends z.ZodType> implements FormValueControl<z.infer<S>> {
  readonly schema = input.required<S>();
  readonly value = model.required<z.infer<S>>();
  readonly disabled = input(false);
  readonly readonly = input(false);

  readonly touch = output<void>();

  readonly innerForm: FieldTree<unknown> = form(
    this.value as unknown as WritableSignal<unknown>,
    (path) => {
      validateStandardSchema(path, () => this.schema());
      disabled(path, { when: () => this.disabled() });
      readonly(path, { when: () => this.readonly() });
    },
  );

  readonly entries = computed(() => objectEntries(this.schema()));
}
