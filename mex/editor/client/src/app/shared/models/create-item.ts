/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import { BaseContactPointSchema } from "../models/generated/contact-point";
import { BaseOrganizationSchema } from "./generated/organization";
import { BasePersonSchema } from "./generated/person";

/**
 * Schema for CreatePerson.
 */
export const CreatePersonSchema = z.object({
  $type: z.literal("CreatePerson"),
  familyName: BasePersonSchema.shape.familyName.unwrap().element.nonempty(),
  givenName: BasePersonSchema.shape.givenName.unwrap().element.nonempty(),
});

/**
 * Model to store data for person creation.
 */
export type CreatePerson = z.infer<typeof CreatePersonSchema>;

/**
 * Schema for CreateContactPoint.
 */
export const CreateContactPointSchema = z.object({
  $type: z.literal("CreateContactPoint"),
  email: BaseContactPointSchema.shape.email.element,
});

/**
 * Model to store data for person creation.
 */
export type CreateContactPoint = z.infer<typeof CreateContactPointSchema>;

/**
 * Schema for CreateOrganization.
 */
export const CreateOrganizationSchema = z.object({
  $type: z.literal("CreateOrganization"),
  officialName: BaseOrganizationSchema.shape.officialName.unwrap().shape.value,
});

/**
 * Model to store data for organization creation.
 */
export type CreateOrganization = z.infer<typeof CreateOrganizationSchema>;

/**
 * UnionType for creatable items.
 */
export type CreateItem = CreatePerson | CreateContactPoint | CreateOrganization;

/**
 * Determines if the given object is a {@link CreateItem}.
 * @param obj Object to check.
 * @returns True of the given object is a {@link CreateItem}; otherwise false.
 */
export function isCreateItem(obj: unknown): obj is CreateItem {
  if (obj && typeof obj == "object" && "$type" in obj) {
    const t = obj["$type"];
    return !!t && typeof t == "string" && t.startsWith("Create");
  }
  return false;
}
