import { Component } from "@angular/core";

import { ToastContent } from "./toast-content/toast-content";

@Component({
  selector: "mex-success-toast",
  imports: [ToastContent],
  template: `<mex-toast-content iconName="check_circle"> </mex-toast-content>`,
})
/**
 * Toast for success.
 */
export class SuccessToast {}
