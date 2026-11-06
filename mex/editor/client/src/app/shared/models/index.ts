/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateContactPointSchema,
  CreateOrganizationSchema,
  CreatePersonSchema,
} from "./create-item";
import { type PreviewContactPoint, PreviewContactPointSchema } from "./generated/contact-point";
import { type PreviewOrganization, PreviewOrganizationSchema } from "./generated/organization";
import type { PreviewOrganizationalUnit } from "./generated/organizational-unit";
import { type PreviewPerson, PreviewPersonSchema } from "./generated/person";
import type { LinkLanguage } from "./generated/shared";
import { LinkLanguageSchema } from "./generated/shared";

/**
 * UnionType for all preview items.
 */
export type PreviewItem =
  PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson | PreviewOrganization;

/**
 * Catgegory for Field.
 */
export type FieldCategory = "optional" | "recommended" | "required";

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
 * Schema for UnionType for CreateOrganization and PreviewOrganization.
 */
export const CreateOrPreviewOrganizationSchema = z.union([
  PreviewOrganizationSchema,
  CreateOrganizationSchema,
]);

/**
 * UnionType for CreateContactPoint and PreviewContactPoint.
 */
export type CreateOrPreviewOrganization = z.infer<typeof CreateOrPreviewOrganizationSchema>;

/**
 * Gives the given string as LinkLanguage. If its not a valid LinkLanuage it will fallback to "de".
 * @param value The given value to give back as LinkLanguage.
 * @returns Returns value as LinkLanguage; if its no valid LinkLanguage it will fallback to "de".
 */
export function asLinkLanguage(value: string): LinkLanguage {
  const result = LinkLanguageSchema.safeParse(value);
  return result.success ? result.data : "de";
}
