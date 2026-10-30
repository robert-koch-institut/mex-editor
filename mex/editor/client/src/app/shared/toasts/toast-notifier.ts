import { inject, Service } from "@angular/core";
import type { MatSnackBarConfig } from "@angular/material/snack-bar";
import { MatSnackBar } from "@angular/material/snack-bar";
import { TranslocoService } from "@jsverse/transloco";

import type { SubmissionError } from "../models/submission-result";
import { ErrorToast } from "./error-toast";
import { SubmissionErrorToast } from "./submission-error-toast";
import { SuccessToast } from "./success-toast";

/**
 * Message as string or transloco message with params.
 */
export type TextMessage = string | { msgKey: string; params?: Record<string, unknown> };

@Service()
/**
 * A Service to easily raise user notifications as a toast/snackbar.
 */
export class ToastNotifier {
  private readonly snackBar = inject(MatSnackBar);
  private readonly transloco = inject(TranslocoService);

  private readonly baseConfig: MatSnackBarConfig = {
    horizontalPosition: "end",
    verticalPosition: "bottom",
  };

  private messageToString(message: TextMessage) {
    if (!(typeof message === "string")) {
      return this.transloco.translate(message.msgKey, message.params);
    }
    return message;
  }

  private toToastTexts(message: TextMessage, title: TextMessage) {
    return {
      title: this.messageToString(title),
      message: this.messageToString(message),
    };
  }

  success(message: TextMessage, title: TextMessage, duration = 4000): void {
    this.snackBar.openFromComponent(SuccessToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "success-toast"],
      data: {
        ...this.toToastTexts(message, title),
      },
    });
  }

  error(message: TextMessage, title: TextMessage, error: Error, duration = 10000): void {
    this.snackBar.openFromComponent(ErrorToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "error-toast"],
      data: {
        ...this.toToastTexts(message, title),
        error,
      },
    });
  }

  submissionError<T extends { $type: string }>(
    message: TextMessage,
    title: TextMessage,
    error: SubmissionError<T>,
    duration = 10000,
  ): void {
    this.snackBar.openFromComponent(SubmissionErrorToast, {
      ...this.baseConfig,
      duration,
      panelClass: ["toast", "error-toast"],
      data: { ...this.toToastTexts(message, title), error },
    });
  }
}
