import { Component, computed, input } from "@angular/core";
import type { FieldTree } from "@angular/forms/signals";
import { MatIcon } from "@angular/material/icon";
import type z from "zod";

import { getFieldKind, unwrapZod } from "../models/zod-types";
import { ZodFieldEditor } from "../zod-field-editor/zod-field-editor";

/**
 *  Leerer Startwert. Signal Forms kennt kein `undefined` als Wert, daher null/''/[].
 * */
export function defaultFor(schema: z.ZodType): unknown {
  switch (getFieldKind(schema)) {
    case "string":
      return "";
    case "boolean":
      return false;
    case "array":
      return [];
    case "object": {
      const shape = (unwrapZod(schema) as z.ZodObject).shape as Record<string, z.ZodType>;
      return Object.fromEntries(Object.entries(shape).map(([k, v]) => [k, defaultFor(v)]));
    }
    default:
      return null; // number, date, enum, unknown
  }
}

@Component({
  selector: "mex-zod-array-editor",
  imports: [MatIcon, ZodFieldEditor],
  templateUrl: "./zod-array-editor.html",
  styleUrl: "./zod-array-editor.scss",
})
/**
 * ZodArrayEditor API documentation.
 */
export class ZodArrayEditor {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readonly field = input.required<FieldTree<any>>();
  readonly schema = input.required<z.ZodType>();
  readonly name = input.required<string>();

  protected readonly element = computed(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    () => (unwrapZod(this.schema()) as any).def.element as z.ZodType,
  );
  protected readonly items = computed(() => this.field() as unknown as FieldTree<unknown[]>);

  protected add(): void {
    this.field()().value.update((arr: unknown) => {
      if (Array.isArray(arr)) {
        const newItem = defaultFor(this.element());
        return [...arr, newItem];
      }
      return null;
    });
  }
  protected remove(index: number): void {
    this.field()().value.update((arr: unknown) => {
      if (Array.isArray(arr)) {
        arr.filter((_, i) => i !== index);
      }
    });
  }
}
