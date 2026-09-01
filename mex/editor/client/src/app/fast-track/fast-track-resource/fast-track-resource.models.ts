/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { CreateContactPointSchema, CreatePersonSchema } from "../../shared/models/create-item";
import { PreviewContactPointSchema } from "../../shared/models/generated/contact-point";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import { PreviewPersonSchema } from "../../shared/models/generated/person";
import {
  FrequencySchema,
  ResourceCreationMethodSchema,
  ResourceTypeGeneralSchema,
} from "../../shared/models/generated/resource";
import { TextSchema, ThemeSchema } from "../../shared/models/generated/shared";
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
  // required fields
  title: TextSchema.shape.value.nonempty(),
  description: TextSchema.shape.value.nonempty(),
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
    en: TextSchema.shape.value.array().nonempty(),
    de: TextSchema.shape.value.array().nonempty(),
  }),
  resourceCreationMethod: ResourceCreationMethodSchema.array().nonempty(),
  accrualPeriodicity: FrequencySchema.nonoptional(),
  provenance: TextSchema.shape.value.nonempty(),
  rights: TextSchema.shape.value.nonempty(),

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
