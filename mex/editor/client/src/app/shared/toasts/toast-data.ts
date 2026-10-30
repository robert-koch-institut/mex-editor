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
export interface ToastErrorData<T extends Error = Error> extends ToastData {
  error: T;
}
