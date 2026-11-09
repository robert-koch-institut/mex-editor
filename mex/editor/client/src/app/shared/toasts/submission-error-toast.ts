import { Component, inject } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { TranslocoDirective } from "@jsverse/transloco";

import { ErrorMailToPipe } from "../error-mail-to-pipe";
import type { SubmissionError } from "../models/submission-result";
import { ToastContent } from "./toast-content/toast-content";
import type { ToastErrorData } from "./toast-data";

@Component({
  selector: "mex-submission-error-toast",
  imports: [ErrorMailToPipe, MatButtonModule, ToastContent, TranslocoDirective],
  styles: ".toast-actions { display: flex; justify-content: flex-end; }",
  template: `
    <mex-toast-content iconName="error">
      <div class="toast-actions" *transloco="let t">
        <a matButton [href]="data.error | errorMailTo" (click)="snackBarRef.dismissWithAction()">
          {{ t("toast.submissionError.sendMail") }}
        </a>
      </div>
    </mex-toast-content>
  `,
})
/**
 * Toast for submission failure.
 */
export class SubmissionErrorToast<T extends { $type: string }> {
  protected readonly data = inject<ToastErrorData<SubmissionError<T>>>(MAT_SNACK_BAR_DATA);
  protected readonly snackBarRef = inject(MatSnackBarRef);
}
