import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

import { getLabel } from "./label-util";
import type { PreviewItem } from "./models";
import type { Concept } from "./models/concept";

@Pipe({
  name: "toLabel",
})
/**
 * Transforms objects to labels.
 */
export class ToLabelPipe implements PipeTransform {
  transform(value: Concept | PreviewItem, lang: string): string {
    return getLabel(value, lang);
  }
}
