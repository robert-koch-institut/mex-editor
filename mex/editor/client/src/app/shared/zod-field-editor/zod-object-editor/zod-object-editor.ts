import { Component, computed, forwardRef, inject, input, model, output } from "@angular/core";
import type { Field, FieldTree, FormValueControl } from "@angular/forms/signals";
import { FormField } from "@angular/forms/signals";
import type z from "zod";

import { FieldCategoryPipe } from "../../field-category-pipe";
import { FieldErrors } from "../../field-errors/field-errors";
import { Fieldset } from "../../fieldset/fieldset";
import { ZodFieldEditor } from "../zod-field-editor";

@Component({
  imports: [FieldCategoryPipe, FieldErrors, Fieldset, forwardRef(() => ZodFieldEditor)],
  selector: "mex-zod-object-editor",
  styleUrl: "./zod-object-editor.scss",
  templateUrl: "./zod-object-editor.html",
})
/**
 * Docs
 */
export class ZodObjectEditor<T extends z.ZodObject> implements FormValueControl<z.infer<T>> {
  readonly schema = input.required<T>();
  readonly value = model.required<z.infer<T>>();

  readonly disabled = input(false);
  readonly readonly = input(false);

  readonly touch = output<void>();

  private readonly formField = inject(FormField<z.infer<T>>);

  readonly entries = computed(() => {
    const shape = this.schema().shape;
    const objField = this.formField.field() as Field<z.infer<T>, string>;
    const objFieldState = objField();
    const objFieldTree = objFieldState.fieldTree as FieldTree<z.infer<T>, string, "writable">;

    return Object.entries(shape).map(([key, schema]) => ({
      key,
      schema,
      field: objFieldTree[key]!,
    }));
  });
}
