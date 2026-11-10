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

/**
 * Class for Error during submission of items including its payload.
 */
export class SubmissionError<T extends { $type: string }> extends Error {
  constructor(
    readonly payload: T,
    readonly innerError?: Error,
  ) {
    super(`Error while submitting '${payload.$type}'`);
  }
}
