/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { CreateOrPreviewContactPointSchema, CreateOrPreviewPersonSchema } from "../shared/models";
import { PreviewOrganizationalUnitSchema } from "../shared/models/generated/organizational-unit";
import { FrequencySchema, ResourceCreationMethodSchema } from "../shared/models/generated/resource";
import { TextSchema, ThemeSchema } from "../shared/models/generated/shared";
import { luxonDateTimeNullableSchema, recommended } from "../shared/models/zod-types";

/**
 * Schema for FasttrackResourceModel
 */
export const FastTrackResourceModelSchema = z.object({
  $type: z.literal("FastTrackResourceModel"),
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
  provenance: TextSchema.shape.value,
  rights: TextSchema.shape.value,

  // recommended fields
  creator: recommended(CreateOrPreviewPersonSchema.array()),
  contributor: recommended(CreateOrPreviewPersonSchema.array()),
  contributingUnit: recommended(PreviewOrganizationalUnitSchema.array()),
  spatial: recommended(z.string()),
  hasLegalBasis: recommended(z.string()),
  start: recommended(luxonDateTimeNullableSchema()),
  end: recommended(luxonDateTimeNullableSchema()),
  theme: recommended(ThemeSchema.array()),
});

/**
 * Model for the Ressource fast track creation page.
 */
export type FastTrackResourceModel = z.infer<typeof FastTrackResourceModelSchema>;
