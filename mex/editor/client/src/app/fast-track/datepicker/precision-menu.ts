import { ChangeDetectionStrategy, Component, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatIcon } from "@angular/material/icon";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { TranslocoPipe } from "@jsverse/transloco";

import type { DatepickerPrecision } from "./precision";

@Component({
  selector: "mex-precision-menu",
  imports: [MatIcon, MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger, TranslocoPipe],
  templateUrl: "./precision-menu.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
/**
 * Icon button with a menu to choose the precision of the datepicker.
 * The precision icons are registered by `datepickerAppInitializer`.
 */
export class PrecisionMenu {
  /** Currently selected precision, shown on the button. */
  readonly precision = input.required<DatepickerPrecision>();
  /** Precisions offered in the menu. */
  readonly options = input.required<readonly DatepickerPrecision[]>();
  readonly disabled = input<boolean>(false);
  readonly precisionSelected = output<DatepickerPrecision>();
}
