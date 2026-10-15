import { inject, Service } from "@angular/core";
import type { MatSnackBarConfig } from "@angular/material/snack-bar";
import { MatSnackBar } from "@angular/material/snack-bar";

import type { SubmissionFailure } from "./models/submission-result";
import { ErrorToast } from "./toasts/error-toast";
import type { ToastData, ToastErrorData, ToastSubmissionFailureData } from "./toasts/models";
import { SubmissionFailureToast } from "./toasts/submission-failure-toast";
import { SuccessToast } from "./toasts/success-toast";

@Service()
/**
 * A Service to easily raise user notifications as a toast/snackbar.
 */
export class ToastNotifier {
  private readonly snackBar = inject(MatSnackBar);

  private readonly baseConfig: MatSnackBarConfig = {
    horizontalPosition: "end",
    verticalPosition: "bottom",
  };

  success(message: string, title: string, duration = 4000): void {
    this.snackBar.openFromComponent(SuccessToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "success-toast"],
      data: { title, message } satisfies ToastData,
    });
  }

  error(message: string, title: string, error: Error, duration = 10000): void {
    this.snackBar.openFromComponent(ErrorToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "error-toast"],
      data: { title, message, error } satisfies ToastErrorData,
    });
  }

  submissionFailure(
    message: string,
    title = "Fehler",
    failure: SubmissionFailure<unknown>,
    duration = 10000,
  ): void {
    this.snackBar.openFromComponent(SubmissionFailureToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "error-toast"],
      data: { title, message, failure } satisfies ToastSubmissionFailureData<unknown>,
    });
  }
}
