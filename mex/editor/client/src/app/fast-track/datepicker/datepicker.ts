import type { Signal } from "@angular/core";
import { ElementRef, signal } from "@angular/core";
import { Component, inject, input, model, output, viewChild } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import { FormsModule } from "@angular/forms";
import type { Field, FormValueControl } from "@angular/forms/signals";
import { form, FormField } from "@angular/forms/signals";
import { ErrorStateMatcher } from "@angular/material/core";
import { DateAdapter } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatHint, MatSuffix } from "@angular/material/select";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { DateTime } from "luxon";

class DatepickerErrorStateMatcher implements ErrorStateMatcher {
  protected defaultErrorStateMatcher = inject(ErrorStateMatcher);

  constructor(protected readonly hasParseError: Signal<boolean>) {}

  isErrorState(_control: FormControl | null, _form: FormGroupDirective | NgForm | null): boolean {
    return this.defaultErrorStateMatcher.isErrorState(_control, _form); // || this.hasParseError();
  }
  isSignalErrorState(field: Field<unknown> | null): boolean {
    const defaultState = this.defaultErrorStateMatcher.isSignalErrorState
      ? this.defaultErrorStateMatcher.isSignalErrorState(field)
      : false;
    return defaultState || this.hasParseError();
  }
}

@Component({
  selector: "mex-datepicker",
  imports: [
    FormField,
    FormsModule,
    MatDatepickerModule,
    MatFormField,
    MatHint,
    MatInput,
    MatSuffix,
    TranslocoPipe,
  ],
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
  readonly hasParseError = signal(false);

  dateAdapter = inject(DateAdapter<DateTime>);
  dateInput = viewChild.required("dateInput", {
    read: ElementRef<HTMLInputElement>,
  }) as Signal<ElementRef<HTMLInputElement>>;

  customErrorMatcher = new DatepickerErrorStateMatcher(this.hasParseError);

  constructor() {
    this.translocoService.langChanges$
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.dateForm().value.update((x) => (x == null ? null : x.plus(0))));
  }

  focus(): void {
    this.dateInput().nativeElement.focus();
  }

  protected onDateInputChanged(inputText: string) {
    const parsed = this.dateAdapter.parse(inputText, this.dateFormats.parse.dateInput);
    this.hasParseError.set(!!inputText && (parsed == null || !parsed.isValid));
  }
}
