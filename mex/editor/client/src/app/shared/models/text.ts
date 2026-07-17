/**
 * Allows only english and german as language tags for `Text` values.
 */
export type RestrictedTextLanguage = "de" | "en";
/**
 * Possible language tags for `Text` values.
 */
export type TextLanguage = RestrictedTextLanguage | "fr" | "es" | "ru";

/**
 * A text item in mex.model.
 */
export interface Text {
  value: string;
  language: TextLanguage;
}
