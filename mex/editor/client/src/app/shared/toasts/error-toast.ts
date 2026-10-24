import { Component } from "@angular/core";

import { ToastContent } from "./toast-content/toast-content";

@Component({
  selector: "mex-error-toast",
  imports: [ToastContent],
  template: `<mex-toast-content iconName="error"> </mex-toast-content>`,
})
/**
 * Toast for error.
 */
export class ErrorToast {}
