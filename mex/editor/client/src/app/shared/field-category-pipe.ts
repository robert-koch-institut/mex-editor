import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { ZodType } from "zod";
import { ZodArray, ZodString } from "zod";

import type { FieldCategory } from "./models";
import { isRecommended } from "./models/zod-types";

@Pipe({
  name: "fieldCategory",
})
/**
 * Transform a zod fieldSchema to its category.
 */
export class FieldCategoryPipe implements PipeTransform {
  private isOptional(fieldSchema: ZodType) {
    if (fieldSchema.safeParse(undefined).success || fieldSchema.safeParse(null).success) {
      return true;
    }

    if (fieldSchema instanceof ZodString) {
      if (fieldSchema.safeParse("").success) {
        return true;
      }
    }

    if (fieldSchema instanceof ZodArray) {
      if (fieldSchema.safeParse([]).success) {
        return true;
      }
    }

    return false;
  }

  transform(fieldSchema: ZodType): FieldCategory {
    if (this.isOptional(fieldSchema)) {
      return isRecommended(fieldSchema) ? "recommended" : "optional";
    }
    return "required";
  }
}
