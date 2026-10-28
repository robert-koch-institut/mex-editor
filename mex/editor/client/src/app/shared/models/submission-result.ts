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
export interface SubmissionFailure {
  success: false;
  error: Error;
}

/**
 * Result of a submission.
 */
export type SubmissionResult<TSubmissionResponse> =
  SubmissionSuccess<TSubmissionResponse> | SubmissionFailure;
