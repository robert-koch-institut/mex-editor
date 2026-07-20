import type { SearchContact } from "./contact-search";
import type { CreateContact } from "./create-contact";

/**
 * Model for the Ressource fast track creation page.
 */
export interface FastTrackResourceModel {
  title: string;
  theme: string[];
  resourceCreationMethod: string[];
  accrualPeriodicity: string | null;
  accessRestriction: string;
  unitInCharge: string[];
  contacts: (CreateContact | SearchContact | string)[];
}
