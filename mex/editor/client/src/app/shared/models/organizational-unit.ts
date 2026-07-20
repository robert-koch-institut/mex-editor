import type { Text } from "./text";

/**
 * Preview for merging all extracted items and rules for an organizational unit.
 */
export interface PreviewOrganizationalUnit {
  $type: "PreviewOrganizationalUnit";
  identifier: string;
  name: Text[];
}
