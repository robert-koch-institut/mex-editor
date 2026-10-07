import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

import type { PreviewItem } from "./models";
import type { BilingualText, Concept } from "./models/concept";
import type { CreateItem } from "./models/create-item";
import type { PreviewContactPoint } from "./models/generated/contact-point";
import type { PreviewOrganizationalUnit } from "./models/generated/organizational-unit";
import type { PreviewPerson } from "./models/generated/person";
import type { Text } from "./models/generated/shared";

@Pipe({
  name: "toLabel",
})
/**
 * Transforms objects to labels.
 */
export class ToLabelPipe implements PipeTransform {
  private pickLabelByLang(values: string | string[] | Text | Text[], lang: string): string | null {
    const valueArray = Array.isArray(values) ? values : [values];
    if (valueArray.length === 0) return null;
    const item = valueArray.at(0);
    if (typeof item == "string") {
      return (valueArray as string[]).filter((x) => !!x).at(0) ?? null;
    }
    return (
      (valueArray as Text[]).filter((x) => x.language === lang).at(0)?.value ??
      (valueArray as Text[]).filter((x) => !x.language).at(0)?.value ??
      null
    );
  }

  private pickLabel(values: string | string[] | Text | Text[]): string | null {
    const valueArray = Array.isArray(values) ? values : [values];
    if (valueArray.length === 0) return null;
    const item = valueArray.at(0);
    if (typeof item == "string") {
      return (valueArray as string[]).filter((x) => !!x).at(0) ?? null;
    }
    return (valueArray as Text[]).filter((x) => x.value).at(0)?.value ?? null;
  }

  private firstLabelOf(values: (string | string[] | Text | Text[] | undefined)[], lang: string) {
    for (const array of values.filter((x) => !!x) as (string | string[] | Text | Text[])[]) {
      const label = this.pickLabelByLang(array, lang) ?? this.pickLabel(array);
      if (label) {
        return label;
      }
    }
    return null;
  }

  private orgUnitToLabel(value: PreviewOrganizationalUnit, lang: string) {
    return this.firstLabelOf(
      [
        value.shortName as string | string[] | Text | Text[] | undefined,
        value.name as string | string[] | Text | Text[] | undefined,
        value.alternativeName as string | string[] | Text | Text[] | undefined,
      ],
      lang,
    );
  }

  private personToLabel(value: PreviewPerson, lang: string) {
    return this.firstLabelOf([value.fullName], lang);
  }

  private contactPointToLabel(value: PreviewContactPoint, lang: string) {
    return this.firstLabelOf([value.email], lang);
  }

  private getConceptLabel(concept: Concept, lang: string) {
    const getTextLabel = (text: BilingualText) => {
      const key = lang as keyof BilingualText;
      if (key in text && text[key]) {
        return text[key];
      }
      return null;
    };
    return (
      getTextLabel(concept.prefLabel) ||
      concept.altLabel
        .map(getTextLabel)
        .filter((x) => !!x)
        .at(0) ||
      concept.identifier
    );
  }

  private defaultPreviewItemLabel(item: PreviewItem) {
    return `${item.$type.replace(/^Preview/, "")} | ${item.identifier}`;
  }

  private defaultCreateItemLabel(item: CreateItem) {
    return item.$type.replace(/^Create/, "");
  }

  transform(value: Concept | PreviewItem | CreateItem, lang: string): string {
    if (!("$type" in value)) {
      return this.getConceptLabel(value, lang);
    }

    switch (value.$type) {
      case "PreviewOrganizationalUnit":
        return this.orgUnitToLabel(value, lang) ?? this.defaultPreviewItemLabel(value);
      case "PreviewPerson":
        return this.personToLabel(value, lang) ?? this.defaultPreviewItemLabel(value);
      case "PreviewContactPoint":
        return this.contactPointToLabel(value, lang) ?? this.defaultPreviewItemLabel(value);
      case "CreateContactPoint":
        return `⋆ ${this.firstLabelOf([value.email], lang) ?? this.defaultCreateItemLabel(value)}`;
      case "CreatePerson":
        return `⋆ ${this.firstLabelOf([`${value.givenName} ${value.familyName}`.trim()], lang) ?? this.defaultCreateItemLabel(value)}`;
    }
  }
}
