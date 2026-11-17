/* eslint-disable @typescript-eslint/naming-convention */
import type z from "zod";

import {
  BaseResourceSchema,
  ExtractedResourceSchema,
} from "../../shared/models/generated/resource";
import { recommended } from "../../shared/models/zod-types";

/**
 * Schema for CreateResourceModel.
 */
export const CreateResourceModelSchema = BaseResourceSchema.extend({
  creator: recommended(ExtractedResourceSchema.shape.creator),
  contributor: recommended(ExtractedResourceSchema.shape.contributor),
  contributingUnit: recommended(ExtractedResourceSchema.shape.contributingUnit),
  healthCategory: recommended(ExtractedResourceSchema.shape.healthCategory),
  temporal: recommended(ExtractedResourceSchema.shape.temporal),
  spatial: recommended(ExtractedResourceSchema.shape.spatial),
  hasLegalBasis: recommended(ExtractedResourceSchema.shape.hasLegalBasis),
});

/**
 * Model for the Resource creation page.
 */
export type CreateResourceModel = z.infer<typeof CreateResourceModelSchema>;
