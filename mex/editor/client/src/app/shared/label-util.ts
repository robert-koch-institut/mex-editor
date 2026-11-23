import type { PreviewItem } from "./models";
import type { BilingualText, Concept } from "./models/concept";
import type { PreviewContactPoint } from "./models/generated/contact-point";
import type { PreviewOrganization } from "./models/generated/organization";
import type { PreviewOrganizationalUnit } from "./models/generated/organizational-unit";
import type { PreviewPerson } from "./models/generated/person";
import type { Text } from "./models/generated/shared";

/**
 * Picks the first valid label value by language.
 * @param values The values to pick the label from.
 * @param lang The language to use for label.
 * @returns The first valid value; null if no valid found.
 */
export function pickLabelByLang(
  values: string | string[] | Text | Text[],
  lang: string,
): string | null {
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

/**
 * Picks the first valid label value.
 * @param values The values to pick the label from.
 * @returns The first valid value; null if no valid found.
 */
export function pickLabel(values: string | string[] | Text | Text[]): string | null {
  const valueArray = Array.isArray(values) ? values : [values];
  if (valueArray.length === 0) return null;
  const item = valueArray.at(0);
  if (typeof item == "string") {
    return (valueArray as string[]).filter((x) => !!x).at(0) ?? null;
  }
  return (valueArray as Text[]).filter((x) => x.value).at(0)?.value ?? null;
}

/**
 * Picks the first valid label value by language.
 * @param values The values to pick the label from.
 * @param lang The language to use for label.
 * @returns The first valid value; null if no valid found.
 */
export function firstLabelOf(
  values: (string | string[] | Text | Text[] | undefined)[],
  lang: string,
) {
  for (const array of values.filter((x) => !!x) as (string | string[] | Text | Text[])[]) {
    const label = pickLabelByLang(array, lang) ?? pickLabel(array);
    if (label) {
      return label;
    }
  }
  return null;
}

/**
 * Gets the label of the given @see PreviewOrganizationalUnit
 * @param value The @see PreviewOrganizationalUnit to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see PreviewOrganizationalUnit by language.
 */
export function orgUnitToLabel(value: PreviewOrganizationalUnit, lang: string) {
  return firstLabelOf(
    [
      value.shortName as string | string[] | Text | Text[] | undefined,
      value.name as string | string[] | Text | Text[] | undefined,
      value.alternativeName as string | string[] | Text | Text[] | undefined,
    ],
    lang,
  );
}

/**
 * Gets the label of the given @see PreviewPerson
 * @param value The @see PreviewPerson to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see PreviewPerson by language.
 */
export function personToLabel(value: PreviewPerson, lang: string) {
  return firstLabelOf([value.fullName], lang);
}

/**
 * Gets the label of the given @see PreviewOrganization
 * @param value The @see PreviewOrganization to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see PreviewOrganization by language.
 */
export function organizationToLabel(value: PreviewOrganization, lang: string) {
  return firstLabelOf([value.officialName, value.shortName, value.alternativeName], lang);
}

/**
 * Gets the label of the given @see PreviewContactPoint
 * @param value The @see PreviewContactPoint to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see PreviewContactPoint by language.
 */
export function contactPointToLabel(value: PreviewContactPoint, lang: string) {
  return firstLabelOf([value.email], lang);
}

/**
 * Gets the label of the given @see Concept
 * @param concept The @see Concept to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see Concept by language.
 */
export function getConceptLabel(concept: Concept, lang: string) {
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

function defaultPreviewItemLabel(item: PreviewItem) {
  return `${item.$type.replace(/^Preview/, "")} | ${item.identifier}`;
}

/**
 * Gets the label of the given @see Concept or @see PreviewItem
 * @param value The @see Concept or @see PreviewItem to get the label from.
 * @param lang The language to use.
 * @returns The label of the given @see Concept or @see PreviewItem by language.
 */
export function getLabel(value: Concept | PreviewItem, lang: string): string {
  if (!("$type" in value)) {
    return getConceptLabel(value, lang);
  }

  switch (value.$type) {
    case "PreviewOrganizationalUnit":
      return orgUnitToLabel(value, lang) ?? defaultPreviewItemLabel(value);
    case "PreviewPerson":
      return personToLabel(value, lang) ?? defaultPreviewItemLabel(value);
    case "PreviewContactPoint":
      return contactPointToLabel(value, lang) ?? defaultPreviewItemLabel(value);
    case "PreviewOrganization":
      return organizationToLabel(value, lang) ?? defaultPreviewItemLabel(value);
  }
}
