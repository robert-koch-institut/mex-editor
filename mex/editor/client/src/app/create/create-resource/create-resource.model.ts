import type z from "zod";

import {
  BaseResourceSchema,
  ExtractedResourceSchema,
} from "../../shared/models/generated/resource";
import { recommended } from "../../shared/models/zod-recommended";
import { reference } from "../../shared/models/zod-reference";
/* eslint-disable @typescript-eslint/naming-convention */

/**
 * Schema for CreateResourceModel.
 */
export const CreateResourceModelSchema = BaseResourceSchema.extend({
  accessPlatform: reference(ExtractedResourceSchema.shape.accessPlatform, [
    "ContactPoint",
    /* TODO(FE): MergedAccessPlatformIdentifier does not exist */
  ]),
  analytics: reference(ExtractedResourceSchema.shape.analytics, [
    "ContactPoint",
    /* TODO(FE): MergedDistributionIdentifier does not exist */
  ]),
  creator: recommended(reference(ExtractedResourceSchema.shape.creator, ["Person"])),
  contact: reference(ExtractedResourceSchema.shape.contact, [
    "Person",
    "ContactPoint",
    "OrganizationalUnit",
  ]),
  contributor: recommended(reference(ExtractedResourceSchema.shape.contributor, ["Person"])),
  contributingUnit: recommended(
    reference(ExtractedResourceSchema.shape.contributingUnit, ["OrganizationalUnit"]),
  ),
  distribution: reference(ExtractedResourceSchema.shape.distribution, [
    "ContactPoint",
    /* TODO(FE): MergedDistributionIdentifier does not exist */
  ]),
  externalPartner: reference(ExtractedResourceSchema.shape.externalPartner, ["Organization"]),
  hasLegalBasis: recommended(ExtractedResourceSchema.shape.hasLegalBasis),
  hasVersion: reference(ExtractedResourceSchema.shape.hasVersion, [
    "ContactPoint",
    /* TODO(FE): MergedResourceIdentifier does not exist */
  ]),
  healthCategory: recommended(ExtractedResourceSchema.shape.healthCategory),
  inSeries: reference(ExtractedResourceSchema.shape.inSeries, [
    "ContactPoint",
    /* TODO(FE): MergedResourceSeriesIdentifier does not exist */
  ]),
  inSeriesFirstResource: reference(ExtractedResourceSchema.shape.inSeriesFirstResource, [
    "ContactPoint",
    /* TODO(FE): MergedResourceSeriesIdentifier does not exist */
  ]),
  inSeriesLastResource: reference(ExtractedResourceSchema.shape.inSeriesLastResource, [
    "ContactPoint",
    /* TODO(FE): MergedResourceSeriesIdentifier does not exist */
  ]),
  isPartOf: reference(ExtractedResourceSchema.shape.isPartOf, [
    "ContactPoint",
    /* TODO(FE): MergedResourceSeriesIdentifier does not exist */
  ]),
  publication: reference(ExtractedResourceSchema.shape.publication, [
    "ContactPoint",
    /* TODO(FE): MergedBibliographicResourceIdentifier does not exist */
  ]),
  publisher: reference(ExtractedResourceSchema.shape.publisher, ["Organization"]),
  relatedResource: reference(ExtractedResourceSchema.shape.relatedResource, [
    "ContactPoint",
    /* TODO(FE): MergedResourceIdentifier does not exist */
  ]),
  temporal: recommended(ExtractedResourceSchema.shape.temporal),
  sample: reference(ExtractedResourceSchema.shape.sample, [
    "ContactPoint",
    /*  TODO(FE): MergedDistributionIdentifier does not exist*/
  ]),
  spatial: recommended(ExtractedResourceSchema.shape.spatial),
  source: reference(ExtractedResourceSchema.shape.source, [
    "ContactPoint",
    /*  TODO(FE): MergedResourceIdentifier does not exist*/
  ]),
  unitInCharge: reference(ExtractedResourceSchema.shape.unitInCharge, ["OrganizationalUnit"]),
  wasGeneratedBy: reference(ExtractedResourceSchema.shape.wasGeneratedBy, [
    "ContactPoint",
    /*  TODO(FE): MergedActivityIdentifier does not exist*/
  ]),
});

/**
 * Model for the Resource creation page.
 */
export type CreateResourceModel = z.infer<typeof CreateResourceModelSchema>;
