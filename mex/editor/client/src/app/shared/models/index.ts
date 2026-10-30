/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { CreateContactPointSchema, CreatePersonSchema } from "./create-item";
import { type PreviewContactPoint, PreviewContactPointSchema } from "./generated/contact-point";
import type { PreviewOrganizationalUnit } from "./generated/organizational-unit";
import { type PreviewPerson, PreviewPersonSchema } from "./generated/person";

/**
 * UnionType for all preview items.
 */
export type PreviewItem = PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson;

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
