import type { SubmissionFailure } from "../models/submission-result";

/**
 * Interface for ToastData.
 */
export interface ToastData {
  title: string;
  message: string;
}

/**
 * Interface for ToastErrorData.
 */
export interface ToastErrorData extends ToastData {
  error?: Error;
}

/**
 * Interface for ToastSubmissionFailureData.
 */
export interface ToastSubmissionFailureData<T> extends ToastData {
  failure: SubmissionFailure<T>;
}
