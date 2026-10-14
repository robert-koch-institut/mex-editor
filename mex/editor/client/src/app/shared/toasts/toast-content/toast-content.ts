import { Component, inject, input } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MatIcon } from "@angular/material/icon";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";

import type { ToastData } from "../models";

@Component({
  selector: "mex-toast-content",
  imports: [MatButtonModule, MatIcon],
  templateUrl: "./toast-content.html",
  styleUrl: "./toast-content.scss",
})
/**
 * Component to display title, icon and message of a toast notification.
 */
export class ToastContent {
  protected readonly data = inject<ToastData>(MAT_SNACK_BAR_DATA);
  protected readonly snackBarRef = inject(MatSnackBarRef);

  iconName = input.required<string>();
}
