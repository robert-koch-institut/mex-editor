/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { CreateContactPointSchema, CreatePersonSchema } from "../../shared/models/create-item";
import { PreviewContactPointSchema } from "../../shared/models/generated/contact-point";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import { PreviewPersonSchema } from "../../shared/models/generated/person";
import {
  // FrequencySchema,
  MergedResourceSchema,
  ResourceTypeGeneralSchema,
} from "../../shared/models/generated/resource";
import { ThemeSchema } from "../../shared/models/generated/shared";
import { luxonDateTimeNullabeSchema } from "../../shared/models/zod-types";

/**
 * Schema for UnionType for CreatePerson and PreviewPerson
 */
export const CreateOrPreviewPersonSchema = z.union([PreviewPersonSchema, CreatePersonSchema]);

/**
 * UnionType for CreatePerson and PreviewPerson.
 */
export type CreateOrPreviewPerson = z.infer<typeof CreateOrPreviewPersonSchema>;

/**
 * Schema for UnionType for CreateContactPoint and PreviewContactPoint.
 */
export const CreateOrPreviewContactPointSchema = z.union([
  PreviewContactPointSchema,
  CreateContactPointSchema,
]);

/**
 * UnionType for CreateContactPoint and PreviewContactPoint.
 */
export type CreateOrPreviewContactPoint = z.infer<typeof CreateOrPreviewContactPointSchema>;

/**
 * Schema for FasttrackResourceModel
 */
export const FastTrackResourceModelSchema = z.object({
  title: MergedResourceSchema.shape.title.element.shape.value,
  description: MergedResourceSchema.shape.description.unwrap().element.shape.value,
  contact: z
    .union([
      CreateOrPreviewPersonSchema,
      CreateOrPreviewContactPointSchema,
      PreviewOrganizationalUnitSchema,
    ])
    .array()
    .nonempty(),
  unitInCharge: PreviewOrganizationalUnitSchema.array().nonempty(),
  keywords: z.object({
    en: MergedResourceSchema.shape.keyword.unwrap().element.shape.value.array().nonempty(),
    de: MergedResourceSchema.shape.keyword.unwrap().element.shape.value.array().nonempty(),
  }),
  resourceCreationMethod: MergedResourceSchema.shape.resourceCreationMethod.unwrap().nonempty(),
  accrualPeriodicity: MergedResourceSchema.shape.accrualPeriodicity.unwrap().unwrap(),
  provenance: MergedResourceSchema.shape.provenance.unwrap().element.shape.value,
  rights: MergedResourceSchema.shape.rights.unwrap().element.shape.value,

  // recommended fields
  creator: CreateOrPreviewPersonSchema.array(),
  contributor: CreateOrPreviewPersonSchema.array(),
  contributingUnit: PreviewOrganizationalUnitSchema.array(),
  spatial: z.string(),
  hasLegalBasis: z.string(),
  start: luxonDateTimeNullabeSchema(),
  end: luxonDateTimeNullabeSchema(),
  resourceTypeGeneral: ResourceTypeGeneralSchema.array(),
  theme: ThemeSchema.array(),
});

/**
 * Model for the Ressource fast track creation page.
 */
export type FastTrackResourceModel = z.infer<typeof FastTrackResourceModelSchema>;
