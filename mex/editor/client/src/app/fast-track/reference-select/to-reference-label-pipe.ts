import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

import { firstLabelOf, getLabel } from "../../shared/label-util";
import type { PreviewItem } from "../../shared/models";
import type { Concept } from "../../shared/models/concept";
import { type CreateItem, isCreateItem } from "../create-item";

@Pipe({
  name: "toReferenceLabel",
  standalone: true,
})
/**
 * Transforms objects to labels.
 */
export class ToReferenceLabelPipe implements PipeTransform {
  private defaultCreateItemLabel(item: CreateItem) {
    return item.$type.replace(/^Create/, "");
  }

  transform(value: Concept | PreviewItem | CreateItem, lang: string): string {
    if (isCreateItem(value)) {
      switch (value.$type) {
        case "CreateContactPoint":
          return `⋆ ${firstLabelOf([value.email], lang) ?? this.defaultCreateItemLabel(value)}`;
        case "CreatePerson":
          return `⋆ ${firstLabelOf([`${value.givenName} ${value.familyName}`.trim()], lang) ?? this.defaultCreateItemLabel(value)}`;
        case "CreateOrganization":
          return `⋆ ${firstLabelOf([`${value.officialName}`.trim()], lang) ?? this.defaultCreateItemLabel(value)}`;
      }
    }
    return getLabel(value, lang);
  }
}
