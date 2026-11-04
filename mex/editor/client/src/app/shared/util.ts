import type { LinkLanguage } from "./models/generated/shared";
import { LinkLanguageSchema } from "./models/generated/shared";

/**
 * Gives the given string as LinkLanguage. If its not a valid LinkLanuage it will fallback to "de".
 * @param value The given value to give back as LinkLanguage.
 * @returns Returns value as LinkLanguage; if its no valid LinkLanguage it will fallback to "de".
 */
export function asLinkLanguage(value: string): LinkLanguage {
  const result = LinkLanguageSchema.safeParse(value);
  return result.success ? result.data : "de";
}
