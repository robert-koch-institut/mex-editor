import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { Concept } from "./models";
import { isCreateItem, type CreateItem, type PreviewItem } from "./models";
import { ToLabelPipe } from "./to-label-pipe";

/**
 * Data as Lookup containing id and label.
 */
export interface Lookup<T> {
  id: string;
  label: string;
  data: T;
}

@Pipe({
  name: "toLookup",
})
/**
 * Pipe to transform data to lookups.
 */
export class ToLookupPipe implements PipeTransform {
  private labelPipe = new ToLabelPipe();

  transform(
    value: Concept | PreviewItem | CreateItem,
    lang: string,
  ): Lookup<Concept | PreviewItem | CreateItem> {
    const label = this.labelPipe.transform(value, lang);
    return {
      id: isCreateItem(value) ? crypto.randomUUID() : value.identifier,
      label: label,
      data: value,
    };
  }
}
