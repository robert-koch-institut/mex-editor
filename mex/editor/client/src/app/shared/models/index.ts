import type { PreviewContactPoint } from "./contact-point";
import type { PreviewOrganizationalUnit } from "./organizational-unit";
import type { PreviewPerson } from "./person";

/**
 * Model for mex.common BilingualText
 */
export interface BilingualText {
  de?: string | null;
  en?: string | null;
}

/**
 * Model for mex.common Concept.
 */
export interface Concept {
  identifier: string;
  inScheme: string;
  prefLabel: BilingualText;
  altLabel: BilingualText[];
  definition?: BilingualText | null;
}

/**
 * UnionType for all preview items.
 */
export type PreviewItem = PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson;

/**
 * UnionType for simple types (excluding prefixes like "Merged", "Extracted" and "Preview")
 */
export type SimpleEntityType =
  "Resource" | "Person" | "ContactPoint" | "Organization" | "OrganizationalUnit";

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
 * UnionType for creatable entities.
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

/**
 * UnionType for CreatePerson and PreviewPerson.
 */
export type CreateOrPreviewPerson = PreviewPerson | CreatePerson;
/**
 * UnionType for CreateContactPoint and PreviewContactPoint.
 */
export type CreateOrPreviewContactPoint = PreviewContactPoint | CreateContactPoint;
