import { Component, inject } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { TranslocoDirective } from "@jsverse/transloco";

import { ErrorMailToPipe } from "../error-mail-to-pipe";
import { ToastContent } from "./toast-content/toast-content";
import type { ToastSubmissionFailureData } from "./toast-data";

@Component({
  selector: "mex-submission-failure-toast",
  imports: [ErrorMailToPipe, MatButtonModule, ToastContent, TranslocoDirective],
  styles: ".toast-actions { display: flex; justify-content: flex-end; }",
  template: `
    <mex-toast-content iconName="error">
      <div class="toast-actions" *transloco="let t">
        <a matButton [href]="data.failure | errorMailTo" (click)="snackBarRef.dismissWithAction()">
          {{ t("fasttrack.resource.toast.submissionFailure.sendMail") }}
        </a>
      </div>
    </mex-toast-content>
  `,
})
/**
 * Toast for submission failure.
 */
export class SubmissionFailureToast {
  protected readonly data = inject<ToastSubmissionFailureData<unknown>>(MAT_SNACK_BAR_DATA);
  protected readonly snackBarRef = inject(MatSnackBarRef);
}
