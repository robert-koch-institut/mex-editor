/**
 * Model for Activity.
 */
export interface Activity {
  $type: "PreviewActivity" | "ExtractedActivity";

  stableTargetId: string;
  identifier: string;
}
