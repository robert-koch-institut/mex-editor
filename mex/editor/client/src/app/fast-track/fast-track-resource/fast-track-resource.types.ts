import type { DateTime } from "luxon";
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
  resourceCreationMethod: string[];
  accrualPeriodicity: string | null;
  spatial: string;
  start: DateTime | null;
  end: DateTime | null;
  hasLegalBasis: string;
  provenance: string;
  rights: string;
  keywords: {
    en: string[];
    de: string[];
  };
  // TODO(fe): not done
  unitInCharge: string[];
  contacts: (CreateContact | SearchContact | string)[];
  creator: string[];
  contributor: string[];
  contributingUnit: string[];
}
