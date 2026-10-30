/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateOrPreviewContactPointSchema,
  CreateOrPreviewPersonSchema,
} from "../../shared/models";
import { ActivityTypeSchema } from "../../shared/models/generated/activity";
import { PreviewOrganizationSchema } from "../../shared/models/generated/organization";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import {
  LinkSchema,
  TextSchema,
  yearMonthDayPattern,
  yearMonthPattern,
  yearPattern,
} from "../../shared/models/generated/shared";

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
  shortName: z.string().optional(),
  involvedPerson: z.array(CreateOrPreviewPersonSchema).optional(),
  involvedUnit: z.array(PreviewOrganizationalUnitSchema).optional(),
  start: z
    .array(
      z.union([
        z.string().regex(new RegExp(yearMonthDayPattern)),
        z.string().regex(new RegExp(yearMonthPattern)),
        z.string().regex(new RegExp(yearPattern)),
      ]),
    )
    .optional(),

  end: z
    .array(
      z.union([
        z.string().regex(new RegExp(yearMonthDayPattern)),
        z.string().regex(new RegExp(yearMonthPattern)),
        z.string().regex(new RegExp(yearPattern)),
      ]),
    )
    .optional(),
  funderOrCommissioner: PreviewOrganizationSchema.array().optional(),
  website: z.array(LinkSchema),

  // optional fields
});

/**
 * Model for the Activity fast track creation page.
 */
export type FastTrackActivityModel = z.infer<typeof FastTrackActivityModelSchema>;
