/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { CreateContactPointSchema, CreatePersonSchema } from "../../shared/models/create-item";
import type { ContactPointRuleSetRequest } from "../../shared/models/generated/contact-point";
import { PreviewContactPointSchema } from "../../shared/models/generated/contact-point";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import type { PersonRuleSetRequest } from "../../shared/models/generated/person";
import { PreviewPersonSchema } from "../../shared/models/generated/person";
import type {
  ResourceRuleSetRequest,
  ResourceRuleSetResponse,
} from "../../shared/models/generated/resource";
import {
  ExtractedResourceSchema,
  FrequencySchema,
  ResourceCreationMethodSchema,
} from "../../shared/models/generated/resource";
import {
  TextSchema,
  ThemeSchema,
  yearMonthDayPattern,
  yearMonthDayTimePattern,
  yearMonthPattern,
  yearPattern,
} from "../../shared/models/generated/shared";
import type {
  SubmissionFailure,
  SubmissionResult,
  SubmissionSuccess,
} from "../../shared/models/submission-result";
import { recommended } from "../../shared/models/zod-types";

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
  start: recommended(
    z
      .union([
        z.string().regex(new RegExp(yearMonthDayTimePattern)).nonempty(),
        z.string().regex(new RegExp(yearMonthDayPattern)).nonempty(),
        z.string().regex(new RegExp(yearMonthPattern)).nonempty(),
        z.string().regex(new RegExp(yearPattern)).nonempty(),
      ])
      .nonoptional(),
  ),
  end: recommended(ExtractedResourceSchema.shape.end.unwrap().element.nullable()),
  theme: recommended(ThemeSchema.array()),
});

/**
 * Model for the Ressource fast track creation page.
 */
export type FastTrackResourceModel = z.infer<typeof FastTrackResourceModelSchema>;

/**
 * Error for submitting fasttrack resource sub items.
 */
export class FastTrackResourceSubPostError extends Error {
  constructor(
    readonly originalError: Error,
    readonly payload: PersonRuleSetRequest | ContactPointRuleSetRequest,
  ) {
    super("Posting a sub item failed.", { cause: originalError });
  }
}

/**
 * Result of a successfull FastTrackResource submission.
 */
export type FastTrackResourceSubmissionSuccess = SubmissionSuccess<ResourceRuleSetResponse>;

/**
 * Result of a failed  FastTrackResource submission.
 */
export type FastTrackResourceSubmissionFailure = SubmissionFailure<ResourceRuleSetRequest>;

/**
 * Result of the FastTrackResource submission.
 */
export type FastTrackResourceSubmissionResult = SubmissionResult<
  ResourceRuleSetResponse,
  ResourceRuleSetRequest
>;
