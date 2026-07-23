import type { SearchContact } from "./contact-search";
import type { CreateContact } from "./create-contact";

/**
 * Model for the Ressource fast track creation page.
 */
export interface FastTrackResourceModel {
  title: string;
  description: string;
  theme: string[];
  resourceTypeGeneral: string[];
  spatial: string[];
  resourceCreationMethod: string[];
  accrualPeriodicity: string | null;
  unitInCharge: string[];
  contacts: (CreateContact | SearchContact | string)[];
  start: Date | null;
  end: Date | null;
  hasLegalBasis: string;
  provenance: string;
  rights: string;
  keywords: {
    en: string[];
    de: string[];
  };
}
