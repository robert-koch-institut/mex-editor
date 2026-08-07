/**
 * Model for mex.common BilingualText
 */
export interface BilingualText {
  de?: string | null;
  en?: string | null;
}

/**
 * Model for mex.common Concept.
 */
export interface Concept {
  identifier: string;
  inScheme: string;
  prefLabel: BilingualText;
  altLabel: BilingualText[];
  definition?: BilingualText | null;
}
