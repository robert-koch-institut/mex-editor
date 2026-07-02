export interface BilingualText {
  de?: string | null;
  en?: string | null;
}

export interface Concept {
  identifier: string;
  inScheme: string;
  prefLabel: BilingualText;
  altLabel: BilingualText[];
  definition?: BilingualText | null;
}

export interface PaginatedItemsContainer<T> {
  items: T[];
  total: number;
}

export interface VocabularyOption {
  id: string;
  label: string;
}
