import { inject, Service } from "@angular/core";
import type { MatSnackBarConfig } from "@angular/material/snack-bar";
import { MatSnackBar } from "@angular/material/snack-bar";

import type { SubmissionError } from "../../fast-track/fast-track-resource/fast-track-resource-submission";
import { ErrorToast } from "./error-toast";
import { SubmissionErrorToast } from "./submission-error-toast";
import { SuccessToast } from "./success-toast";
import type { ToastData } from "./toast-data";

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
      data: { title, message, error },
    });
  }

  submissionError<T extends { $type: string }>(
    message: string,
    title: string,
    error: SubmissionError<T>,
    duration = 10000,
  ): void {
    this.snackBar.openFromComponent(SubmissionErrorToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "error-toast"],
      data: { title, message, error },
    });
  }
}
