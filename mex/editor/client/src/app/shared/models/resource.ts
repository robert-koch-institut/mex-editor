/**
 * Model for Resource.
 */
export interface Resource {
  $type: "PreviewResource" | "ExtractedResource";

  stableTargetId: string;
  identifier: string;
}
