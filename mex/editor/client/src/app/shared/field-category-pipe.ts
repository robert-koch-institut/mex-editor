import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { ZodType } from "zod";
import { ZodArray, ZodString } from "zod";

import type { FieldCategory } from "./models";

@Pipe({
  name: "fieldCategory",
})
/**
 * Transform a zod fieldSchema to its category.
 */
export class FieldCategoryPipe implements PipeTransform {
  transform(fieldSchema: ZodType): FieldCategory {
    if (fieldSchema.safeParse(undefined).success || fieldSchema.safeParse(null).success) {
      return "optional";
    }

    if (fieldSchema instanceof ZodString) {
      if (fieldSchema.safeParse("").success) {
        return "optional";
      }
    }

    if (fieldSchema instanceof ZodArray) {
      if (fieldSchema.safeParse([]).success) {
        return "optional";
      }
    }

    return "required";
  }
}
