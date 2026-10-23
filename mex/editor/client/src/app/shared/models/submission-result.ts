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
export interface SubmissionFailure<T> {
  success: false;
  payload: T;
  error: Error;
}

/**
 * Result of a submission.
 */
export type SubmissionResult<TResponse = unknown, TPayload = unknown> =
  SubmissionSuccess<TResponse> | SubmissionFailure<TPayload>;
