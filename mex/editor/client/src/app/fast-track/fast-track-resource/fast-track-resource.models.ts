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
  FrequencySchema,
  ResourceCreationMethodSchema,
} from "../../shared/models/generated/resource";
import { TextSchema, ThemeSchema } from "../../shared/models/generated/shared";
import type {
  SubmissionFailure,
  SubmissionResult,
  SubmissionSuccess,
} from "../../shared/models/submission-result";
import { luxonDateTimeNullableSchema, recommended } from "../../shared/models/zod-types";

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
  start: recommended(luxonDateTimeNullableSchema()),
  end: recommended(luxonDateTimeNullableSchema()),
  // resourceTypeGeneral: recommended(ResourceTypeGeneralSchema.array()),
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
