import type { Signal } from "@angular/core";
import { ElementRef, signal } from "@angular/core";
import { Component, inject, input, model, output, viewChild } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import { FormsModule } from "@angular/forms";
import type { Field, FormValueControl } from "@angular/forms/signals";
import { form, FormField } from "@angular/forms/signals";
import type { ErrorStateMatcher, MatDateFormats } from "@angular/material/core";
import { DateAdapter } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatHint, MatSuffix } from "@angular/material/select";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { DateTime } from "luxon";

/**
 * ErrorMatcher to fake the MatDatepickerParse behaviour in a more consistent way.
 */
export class ImmediateErrorStateMatcher implements ErrorStateMatcher {
  protected readonly inputTextElement: Signal<ElementRef<HTMLInputElement>>;
  protected readonly dateAdapter: DateAdapter<DateTime<boolean>>;
  protected readonly dateFormats: MatDateFormats;
  protected readonly parentFormField: FormField<unknown>;

  readonly hasParseError = signal(false);
  readonly hasParentError = signal(false);

  constructor(
    inputTextElement: Signal<ElementRef<HTMLInputElement>>,
    dateAdapter: DateAdapter<DateTime>,
    dateFormats: MatDateFormats,
    parentFormField: FormField<unknown>,
  ) {
    this.inputTextElement = inputTextElement;
    this.dateAdapter = dateAdapter;
    this.dateFormats = dateFormats;
    this.parentFormField = parentFormField;
  }

  isErrorState(_control: FormControl | null, _form: FormGroupDirective | NgForm | null): boolean {
    return this.isSignalErrorState(null);
  }

  isSignalErrorState(field: Field<unknown> | null): boolean {
    const inputText = this.inputTextElement().nativeElement.value;
    const parsed = this.dateAdapter.parse(inputText, this.dateFormats.parse.dateInput);

    const hasParentErrors = this.parentFormField.errors().length > 0;
    const isTouched = (field ?? (() => null))()?.touched() ?? true;
    const parentError = isTouched && hasParentErrors;
    this.hasParentError.set(parentError);

    if (inputText) {
      const parseError = parsed == null || !parsed.isValid;
      this.hasParseError.set(parseError);
      return parseError;
    }

    this.hasParseError.set(false);
    return parentError;
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
  readonly touch = output<void>();

  readonly minDate = input<DateTime | null>(null);
  readonly maxDate = input<DateTime | null>(null);

  protected readonly dateForm = form(this.value);

  dateAdapter = inject(DateAdapter<DateTime>);
  dateInput = viewChild.required("dateInput", {
    read: ElementRef<HTMLInputElement>,
  });
  customErrorMatcher = new ImmediateErrorStateMatcher(
    this.dateInput,
    this.dateAdapter,
    this.dateFormats,
    this.hostFormField,
  );

  constructor() {
    this.translocoService.langChanges$
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.dateForm().value.update((x) => (x == null ? null : x.plus(0))));
  }
}
