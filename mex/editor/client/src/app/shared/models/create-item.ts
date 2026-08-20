/**
 * Model to store data for person creation.
 */
export interface CreatePerson {
  $type: "CreatePerson";
  familyName: string;
  givenName: string;
}

/**
 * Model to store data for person creation.
 */
export interface CreateContactPoint {
  $type: "CreateContactPoint";
  email: string;
}

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
