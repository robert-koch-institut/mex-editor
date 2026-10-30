/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateOrPreviewContactPointSchema,
  CreateOrPreviewPersonSchema,
} from "../../shared/models";
import { ActivityTypeSchema } from "../../shared/models/generated/activity";
import { PreviewOrganizationSchema } from "../../shared/models/generated/organization";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import { LinkSchema, TextSchema } from "../../shared/models/generated/shared";
import { luxonDateTimeNullableSchema } from "../../shared/models/zod-types";

/**
 * Schema for FasttrackActivityModel
 */
export const FastTrackActivityModelSchema = z.object({
  // required fields
  title: TextSchema.shape.value,
  abstract: TextSchema.shape.value,
  contact: z
    .union([
      CreateOrPreviewPersonSchema,
      CreateOrPreviewContactPointSchema,
      PreviewOrganizationalUnitSchema,
    ])
    .array()
    .nonempty(),
  responsibleUnit: z.array(PreviewOrganizationalUnitSchema).nonempty(),
  activityType: z.array(ActivityTypeSchema),

  // recommended fields
  shortName: z.string(),
  involvedPerson: z.array(CreateOrPreviewPersonSchema),
  involvedUnit: z.array(PreviewOrganizationalUnitSchema),
  start: luxonDateTimeNullableSchema(),
  end: luxonDateTimeNullableSchema(),
  funderOrCommissioner: PreviewOrganizationSchema.array(),
  website: z.array(LinkSchema),

  // optional fields
});

/**
 * Model for the Activity fast track creation page.
 */
export type FastTrackActivityModel = z.infer<typeof FastTrackActivityModelSchema>;
