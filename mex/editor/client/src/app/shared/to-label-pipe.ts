import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { Text } from "./models";
import type { PreviewOrganizationalUnit } from "./models/organizational-unit";
import type { PreviewPerson } from "./models/person";
import type { PreviewContactPoint } from "./models/contact-point";
import type { PreviewItem } from "./models";
import type { CreateItem } from "./models/create-item";
import type { BilingualText, Concept } from "./models/concept";

@Pipe({
  name: "toLabel",
})
/**
 * Transforms objects to labels.
 */
export class ToLabelPipe implements PipeTransform {
  private pickLabelByLang(values: string | string[] | Text[], lang: string): string | null {
    if (typeof values === "string") return values;
    if (values.length === 0) return null;
    const item = values.at(0);
    if (typeof item == "string") {
      return (values as string[]).filter((x) => !!x).at(0) ?? null;
    }
    return (
      (values as Text[]).filter((x) => x.language === lang).at(0)?.value ??
      (values as Text[]).filter((x) => !x.language).at(0)?.value ??
      null
    );
  }

  private pickLabel(values: string | string[] | Text[]): string | null {
    if (typeof values === "string") return values;
    if (values.length === 0) return null;
    const item = values.at(0);
    if (typeof item == "string") {
      return (values as string[]).filter((x) => !!x).at(0) ?? null;
    }
    return (values as Text[]).filter((x) => x.value).at(0)?.value ?? null;
  }

  private firstLabelOf(values: (string | string[] | Text[] | undefined)[], lang: string) {
    for (const array of values.filter((x) => !!x) as (string | string[] | Text[])[]) {
      const label = this.pickLabelByLang(array, lang) ?? this.pickLabel(array);
      if (label) {
        return label;
      }
    }
    return null;
  }

  private orgUnitToLabel(value: PreviewOrganizationalUnit, lang: string) {
    return this.firstLabelOf([value.shortName, value.name, value.alternativeName], lang);
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
      return undefined;
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

  transform(value: Concept | PreviewItem | CreateItem, lang: string): string {
    let label: null | string = null;
    if (!("$type" in value)) {
      label = this.getConceptLabel(value, lang);
    } else {
      switch (value.$type) {
        case "PreviewOrganizationalUnit":
          label = this.orgUnitToLabel(value, lang);
          break;
        case "PreviewPerson":
          label = this.personToLabel(value, lang);
          break;
        case "PreviewContactPoint":
          label = this.contactPointToLabel(value, lang);
          break;
        case "CreateContactPoint":
          label = this.firstLabelOf([`⋆ ${value.email}`], lang);
          break;
        case "CreatePerson":
          label = this.firstLabelOf([`⋆ ${value.givenName} ${value.familyName}`], lang);
          break;
      }
    }
    if (!label) {
      throw new Error("Cant create label for", { cause: { value, lang } });
    }
    return label;
  }
}
