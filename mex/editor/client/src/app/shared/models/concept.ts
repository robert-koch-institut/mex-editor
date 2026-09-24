/**
 * Model for mex.editor BilingualText
 */
export interface BilingualText {
  de?: string | null;
  en?: string | null;
}

/**
 * Model for mex.editor Concept.
 */
export interface Concept {
  identifier: string;
  prefLabel: BilingualText;
  altLabel: BilingualText[];
}
