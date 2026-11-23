import { type PreviewContactPoint } from "./generated/contact-point";
import { type PreviewOrganization } from "./generated/organization";
import type { PreviewOrganizationalUnit } from "./generated/organizational-unit";
import { type PreviewPerson } from "./generated/person";
import type { LinkLanguage, TextLanguage } from "./generated/shared";
import { LinkLanguageSchema, TextLanguageSchema } from "./generated/shared";

/**
 * UnionType for all preview items.
 */
export type PreviewItem =
  PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson | PreviewOrganization;

/**
 * Catgegory for Field.
 */
export type FieldCategory = "optional" | "recommended" | "required";

/**
 * Gives the given string as LinkLanguage. If its not a valid LinkLanguage it will fallback to "de".
 * @param value The given value to give back as LinkLanguage.
 * @returns Returns value as LinkLanguage; if its no valid LinkLanguage it will fallback to "de".
 */
export function asLinkLanguage(value: string): LinkLanguage {
  const result = LinkLanguageSchema.safeParse(value);
  return result.success ? result.data : "de";
}

/**
 * Gives the given string as TextLanguage. If its not a valid TextLanguage it will fallback to "de".
 * @param value The given value to give back as TextLanguage.
 * @returns Returns value as TextLanguage; if its no valid TextLanguage it will fallback to "de".
 */
export function asTextLanguage(value: string): TextLanguage {
  const result = TextLanguageSchema.safeParse(value);
  return result.success ? result.data : "de";
}
