/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateOrPreviewContactPointSchema,
  CreateOrPreviewPersonSchema,
} from "../../shared/models";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import {
  FrequencySchema,
  ResourceCreationMethodSchema,
  ResourceTypeGeneralSchema,
} from "../../shared/models/generated/resource";
import { TextSchema, ThemeSchema } from "../../shared/models/generated/shared";
import { luxonDateTimeNullableSchema } from "../../shared/models/zod-types";

/**
 * Schema for FasttrackResourceModel
 */
export const FastTrackResourceModelSchema = z.object({
  // required fields
  title: TextSchema.shape.value,
  description: TextSchema.shape.value,
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
  start: luxonDateTimeNullableSchema(),
  end: luxonDateTimeNullableSchema(),
  resourceTypeGeneral: ResourceTypeGeneralSchema.array(),
  theme: ThemeSchema.array(),
});

/**
 * Model for the Ressource fast track creation page.
 */
export type FastTrackResourceModel = z.infer<typeof FastTrackResourceModelSchema>;
