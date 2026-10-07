import type { PreviewContactPoint } from "./generated/contact-point";
import type { PreviewOrganizationalUnit } from "./generated/organizational-unit";
import type { PreviewPerson } from "./generated/person";

/**
 * UnionType for all preview items.
 */
export type PreviewItem = PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson;

/**
 * Catgegory for Field.
 */
export type FieldCategory = "optional" | "recommended" | "required";
