/* eslint-disable @typescript-eslint/naming-convention */

import type { DateTime } from "luxon";
import type { PreviewOrganizationalUnit } from "../../shared/models/organizational-unit";
import type { PreviewContactPoint } from "../../shared/models/contact-point";
import type { CreatePerson, CreateContactPoint } from "../../shared/models/create-item";
import type { PreviewPerson } from "../../shared/models/person";
import z from "zod";
import { AdditiveResourceSchema } from "../../shared/zod-test/resource/additive-resource";

/**
 * UnionType for CreatePerson and PreviewPerson.
 */
export type CreateOrPreviewPerson = PreviewPerson | CreatePerson;

/**
 * UnionType for CreateContactPoint and PreviewContactPoint.
 */
export type CreateOrPreviewContactPoint = PreviewContactPoint | CreateContactPoint;

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

/**
 * Schema for FasttrackResourceModel
 */
export const FastTrackResourceModelSchema = z.object({
  title: AdditiveResourceSchema.shape.title.unwrap().element,
});
