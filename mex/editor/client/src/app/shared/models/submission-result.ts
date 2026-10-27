import type { SubmissionError } from "../../fast-track/fast-track-resource/fast-track-resource-submission";

/**
 * Result of a successfull submission.
 */
export interface SubmissionSuccess<T> {
  success: true;
  response: T;
}

/**
 * Result of a failed submission.
 */
export interface SubmissionFailure<T extends { $type: string }> {
  success: false;
  error: SubmissionError<T>;
}

/**
 * Result of a submission.
 */
export type SubmissionResult<TSubmissionResponse, TPayload extends { $type: string }> =
  SubmissionSuccess<TSubmissionResponse> | SubmissionFailure<TPayload>;
