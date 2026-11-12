/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateOrPreviewContactPointSchema,
  CreateOrPreviewOrganizationSchema,
  CreateOrPreviewPersonSchema,
} from "../shared/models";
import { ActivityTypeSchema, ExtractedActivitySchema } from "../shared/models/generated/activity";
import { PreviewOrganizationalUnitSchema } from "../shared/models/generated/organizational-unit";
import { LinkSchema, TextSchema } from "../shared/models/generated/shared";
import { recommended } from "../shared/models/zod-types";

/**
 * Schema for FasttrackActivityModel
 */
export const FastTrackActivityModelSchema = z.object({
  $type: z.literal("FastTrackActivityModel"),
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
  shortName: recommended(z.string()),
  involvedPerson: recommended(z.array(CreateOrPreviewPersonSchema)),
  involvedUnit: recommended(z.array(PreviewOrganizationalUnitSchema)),
  start: recommended(ExtractedActivitySchema.shape.start.unwrap().element.nullable()),
  end: recommended(ExtractedActivitySchema.shape.end.unwrap().element.nullable()),
  funderOrCommissioner: recommended(CreateOrPreviewOrganizationSchema.array()),
  website: recommended(z.array(LinkSchema)),

  // optional fields
});

/**
 * Model for the Activity fast track creation page.
 */
export type FastTrackActivityModel = z.infer<typeof FastTrackActivityModelSchema>;
