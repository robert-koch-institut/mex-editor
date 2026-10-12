import type { Signal } from "@angular/core";
import { ElementRef } from "@angular/core";
import { Component, inject, input, model, output, viewChild } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import { FormsModule } from "@angular/forms";
import type { FormValueControl } from "@angular/forms/signals";
import { form, FormField, transformedValue } from "@angular/forms/signals";
import type { ErrorStateMatcher } from "@angular/material/core";
import { DateAdapter } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatSuffix } from "@angular/material/select";
import { TranslocoService } from "@jsverse/transloco";
import type { DateTime } from "luxon";

/**
 * ErrorMatcher to show the errors of the parent form field (incl. parse errors) immediately.
 */
export class ImmediateErrorStateMatcher implements ErrorStateMatcher {
  protected readonly parentFormField: FormField<unknown>;

  constructor(parentFormField: FormField<unknown>) {
    this.parentFormField = parentFormField;
  }

  isErrorState(_control: FormControl | null, _form: FormGroupDirective | NgForm | null): boolean {
    return this.parentFormField.errors().length > 0;
  }
}

@Component({
  selector: "mex-datepicker",
  imports: [FormField, FormsModule, MatDatepickerModule, MatFormField, MatInput, MatSuffix],
  templateUrl: "./datepicker.html",
  styleUrl: "./datepicker.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
/**
 * Wrapper Component for MatDatepicker to simplify usage and handle matDatepickerParse error.
 */
export class Datepicker implements FormValueControl<DateTime | null> {
  protected dateFormats = inject(MAT_DATE_FORMATS);
  protected hostFormField = inject(FormField);
  protected translocoService = inject(TranslocoService);

  readonly value = model<DateTime<boolean> | null>(null);
  readonly disabled = input<boolean>(false);
  readonly readonly = input<boolean>(false);
  readonly touch = output<void>();

  readonly minDate = input<DateTime | null>(null);
  readonly maxDate = input<DateTime | null>(null);

  protected readonly dateForm = form(this.value);

  dateAdapter = inject(DateAdapter<DateTime>);
  dateInput = viewChild.required("dateInput", {
    read: ElementRef<HTMLInputElement>,
  }) as Signal<ElementRef<HTMLInputElement>>;
  // only reports parse errors to the parent form field, the value itself is set by MatDatepickerInput
  protected readonly inputText = transformedValue(this.value, {
    parse: (inputText: string) => {
      const parsed = inputText
        ? this.dateAdapter.parse(inputText, this.dateFormats.parse.dateInput)
        : null;
      const hasParseError = !!inputText && (parsed == null || !parsed.isValid);
      return {
        error: hasParseError
          ? {
              kind: "parse",
              message: "datepicker.validation.parse",
              issue: { format: this.dateFormats.parse.dateInput },
            }
          : undefined,
      };
    },
    format: (value) =>
      value?.isValid ? this.dateAdapter.format(value, this.dateFormats.display.dateInput) : "",
  });
  customErrorMatcher = new ImmediateErrorStateMatcher(this.hostFormField);

  constructor() {
    this.translocoService.langChanges$
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.dateForm().value.update((x) => (x == null ? null : x.plus(0))));
  }

  focus(): void {
    this.dateInput().nativeElement.focus();
  }
}
