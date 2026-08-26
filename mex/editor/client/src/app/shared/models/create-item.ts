/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

/**
 * Schema for CreatePerson.
 */
export const CreatePersonSchema = z.object({
  $type: z.literal("CreatePerson"),
  familyName: z.string().nonempty(),
  givenName: z.string().nonempty(),
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
  email: z.string().nonempty(),
});

/**
 * Model to store data for person creation.
 */
export type CreateContactPoint = z.infer<typeof CreateContactPointSchema>;

/**
 * UnionType for creatable items.
 */
export type CreateItem = CreatePerson | CreateContactPoint;

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
