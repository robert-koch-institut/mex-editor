import type { SearchContact } from "../services/contact-search";
import type { CreateContact } from "./create-contact";

export interface FastTrackResourceModel {
  title: string;
  theme: string[];
  resourceCreationMethod: string[];
  accrualPeriodicity: string | null;
  accessRestriction: string;
  unitInCharge: string[];
  contacts: (CreateContact | SearchContact | string)[];
}
