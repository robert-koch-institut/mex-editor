import { Component, computed, input } from "@angular/core";
import { type FieldTree, FormField } from "@angular/forms/signals";
import type { z } from "zod";

import { Datepicker } from "../../fast-track/datepicker/datepicker";
import { Fieldset } from "../../fast-track/fieldset/fieldset";
import { FieldCategoryPipe } from "../field-category-pipe";
import { getFieldKind } from "../models/zod-types";
import { ZodArrayEditor } from "../zod-array-editor/zod-array-editor";

@Component({
  selector: "mex-zod-field-editor",
  imports: [Datepicker, FieldCategoryPipe, Fieldset, FormField, ZodArrayEditor],
  templateUrl: "./zod-field-editor.html",
  styleUrl: "./zod-field-editor.scss",
})
/**
 * ZodFieldEditor API documentation.
 */
export class ZodFieldEditor {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readonly field = input.required<FieldTree<any>>();
  readonly schema = input.required<z.ZodType>();
  readonly name = input.required<string>();

  protected readonly kind = computed(() => getFieldKind(this.schema()));
  // readonly fieldAsArray = computed(() => this.field() as FieldTree<T[]>);
}
