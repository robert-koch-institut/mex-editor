import type { DateTime } from "luxon";
import type { PreviewOrganizationalUnit } from "../../shared/models/organizational-unit";
import type { CreateOrPreviewContactPoint, CreateOrPreviewPerson } from "../../shared/models";

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
  unitInCharge: PreviewOrganizationalUnit[];
  contributingUnit: PreviewOrganizationalUnit[];
  creator: CreateOrPreviewPerson[];
  contributor: CreateOrPreviewPerson[];
  contacts: (CreateOrPreviewPerson | CreateOrPreviewContactPoint | PreviewOrganizationalUnit)[];
}
