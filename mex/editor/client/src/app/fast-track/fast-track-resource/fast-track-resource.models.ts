/* eslint-disable @typescript-eslint/naming-convention */

import { DateTime } from "luxon";
import z from "zod";

import { CreateContactPointSchema, CreatePersonSchema } from "../../shared/models/create-item";
import { PreviewContactPointSchema } from "../../shared/models/generated/contact-point";
import { PreviewOrganizationalUnitSchema } from "../../shared/models/generated/organizational-unit";
import { PreviewPersonSchema } from "../../shared/models/generated/person";
import { MergedResourceSchema } from "../../shared/models/generated/resource";

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
 * LuxonDateTime as zod type.
 */
export const luxonDateTimeSchema = () =>
  z
    .custom<DateTime>((val) => DateTime.isDateTime(val), {
      error: "validation.required", // null/undefined → leeres Feld
    })
    .refine((val) => val.isValid, {
      error: "validation.invalidDate", // Instanz vorhanden, aber Parse fehlgeschlagen
    });

/**
 * LuxonDateTime and nullable as zod type.
 */
export const luxonDateTimeNullabeSchema = () =>
  z
    .custom<DateTime | null>((val) => val == null || DateTime.isDateTime(val), {
      error: "validation.invalidDate", // null/undefined → leeres Feld
    })
    .nullable();

/**
 * Schema for FasttrackResourceModel
 */
export const FastTrackResourceModelSchema = z.object({
  title: MergedResourceSchema.shape.title.element.shape.value,
  description: MergedResourceSchema.shape.description.unwrap().element.shape.value,
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
    en: MergedResourceSchema.shape.keyword.unwrap().element.shape.value.array().nonempty(),
    de: MergedResourceSchema.shape.keyword.unwrap().element.shape.value.array().nonempty(),
  }),
  resourceCreationMethod: MergedResourceSchema.shape.resourceCreationMethod.unwrap().nonempty(),
  accrualPeriodicity: MergedResourceSchema.shape.accrualPeriodicity
    .unwrap()
    .nullable()
    .refine((x) => x ?? false, { message: "validation.required" }),
  provenance: MergedResourceSchema.shape.provenance.unwrap().element.shape.value,
  rights: MergedResourceSchema.shape.rights.unwrap().element.shape.value,

  // recommended fields
  creator: CreateOrPreviewPersonSchema.array(),
  contributor: CreateOrPreviewPersonSchema.array(),
  contributingUnit: PreviewOrganizationalUnitSchema.array(),
  spatial: MergedResourceSchema.shape.spatial.unwrap().element.shape.value,
  hasLegalBasis: MergedResourceSchema.shape.hasLegalBasis.unwrap().element.shape.value,
  start: luxonDateTimeSchema(),
  end: luxonDateTimeNullabeSchema(),
  resourceTypeGeneral: MergedResourceSchema.shape.resourceTypeGeneral.unwrap(),
  theme: MergedResourceSchema.shape.theme,
});

/**
 * Model for the Ressource fast track creation page.
 */
export type FastTrackResourceModel = z.infer<typeof FastTrackResourceModelSchema>;
