import type { PreviewContactPoint } from "./contact-point";
import type { PreviewOrganizationalUnit } from "./organizational-unit";
import type { PreviewPerson } from "./person";

/**
 * UnionType for all preview items.
 */
export type PreviewItem = PreviewOrganizationalUnit | PreviewContactPoint | PreviewPerson;
