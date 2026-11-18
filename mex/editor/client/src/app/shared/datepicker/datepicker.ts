import type { ElementRef, Signal } from "@angular/core";
import {
  Component,
  computed,
  inject,
  input,
  linkedSignal,
  model,
  output,
  signal,
  viewChild,
} from "@angular/core";
import { takeUntilDestroyed, toSignal } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import type { Field, FieldState, FormValueControl } from "@angular/forms/signals";
import {
  disabled as disableField,
  form,
  FormField,
  readonly as makeReadonly,
} from "@angular/forms/signals";
import type { MatDateFormats } from "@angular/material/core";
import { DateAdapter, ErrorStateMatcher, MAT_DATE_FORMATS } from "@angular/material/core";
import type { MatDatepicker, MatDatepickerInputEvent } from "@angular/material/datepicker";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormField, MatHint, MatPrefix, MatSuffix } from "@angular/material/form-field";
import { MatInput } from "@angular/material/input";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";

import type { DatepickerPrecision } from "./precision";
import {
  ALL_PRECISIONS,
  applyPrecision,
  parseValue,
  resolvePrecision,
  resolvePrecisionFromText,
  serializeValue,
} from "./precision";
import { PrecisionMenu } from "./precision-menu";

export type { DatepickerPrecision } from "./precision";

@Component({
  selector: "mex-datepicker",
  imports: [
    FormField,
    MatDatepickerModule,
    MatFormField,
    MatHint,
    MatInput,
    MatPrefix,
    MatSuffix,
    PrecisionMenu,
    TranslocoPipe,
  ],
  providers: [
    {
      provide: MAT_DATE_FORMATS,
      useFactory: () => new PrecisionDateFormats(inject(MAT_DATE_FORMATS, { skipSelf: true })),
    },
  ],
  templateUrl: "./datepicker.html",
  styleUrl: "./datepicker.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
/**
 * Wrapper für MatDatepicker. Value ist ein String in einem von vier Formaten
 * (YYYY, YYYY-MM, YYYY-MM-DD, Datum+Zeit in UTC); der Editiermodus folgt dem Format.
 */
export class Datepicker implements FormValueControl<string | null> {
  private readonly dateAdapter = inject(DateAdapter<DateTime>);
  private readonly hostFormField = inject(FormField);
  private readonly translocoService = inject(TranslocoService);
  protected readonly formats = inject(MAT_DATE_FORMATS) as PrecisionDateFormats;

  readonly value = model<string | null>(null);
  readonly disabled = input<boolean>(false);
  readonly readonly = input<boolean>(false);
  readonly touch = output<void>();

  readonly minDate = input<DateTime | null>(null);
  readonly maxDate = input<DateTime | null>(null);

  /** Precisions the user may choose from. An empty list allows all precisions. */
  readonly allowedPrecisions = input<readonly DatepickerPrecision[]>(ALL_PRECISIONS);
  /** Preferred precision while no value is set. */
  readonly precision = input<DatepickerPrecision | null>(null);

  protected readonly allowed = computed(() => {
    const list = this.allowedPrecisions();
    return list.length ? list : ALL_PRECISIONS;
  });

  protected readonly showPrecisionSelector = computed(() => this.allowed().length > 1);

  protected readonly mode = linkedSignal<
    {
      value: string | null;
      precision: DatepickerPrecision | null;
      allowed: readonly DatepickerPrecision[];
    },
    DatepickerPrecision
  >({
    source: () => ({
      value: this.value(),
      precision: this.precision(),
      allowed: this.allowed(),
    }),
    computation: ({ value, precision, allowed }, previous) =>
      resolvePrecision(value, [previous?.value, precision], allowed),
  });

  protected readonly startView = computed(() =>
    this.mode() === "year" || this.mode() === "month" ? "multi-year" : "month",
  );

  private readonly activeLang = toSignal(this.translocoService.langChanges$);

  /** Input format of the current precision, re-evaluated when the language changes. */
  protected readonly inputFormat = computed<string>(() => {
    this.activeLang();
    return this.formats.parse.dateInput;
  });

  private readonly parsed = computed(() => parseValue(this.value()));

  /**
   * Date shown in the picker input. Our own emissions are not written back,
   * otherwise partial input would be overwritten while typing.
   */
  private lastEmitted: string | null = null;
  protected readonly pickerValue = linkedSignal<string | null, DateTime | null>({
    source: this.value,
    computation: (value, previous) =>
      previous && value === this.lastEmitted ? previous.value : parseValue(value),
  });

  /**
   * Internal date as signal form, so the error state matcher receives a field.
   * The form owns disabled/readonly of the date input, bindings on the input itself are ignored.
   */
  protected readonly dateForm = form(this.pickerValue, (path) => {
    disableField(path, { when: () => this.disabled() });
    makeReadonly(path, { when: () => this.readonly() });
  });

  /** Time field (HH:mm, UTC). Kept while no date is set yet. */
  protected readonly time = linkedSignal<DateTime | null, string>({
    source: this.parsed,
    computation: (date) => date?.toFormat("HH:mm") ?? "",
  });

  protected readonly hasParseError = signal(false);

  protected readonly customErrorMatcher = new DatepickerErrorStateMatcher(
    this.hasParseError,
    this.hostFormField.state,
  );

  private readonly dateInput = viewChild.required<ElementRef<HTMLInputElement>>("dateInput");

  constructor() {
    this.formats.bindPrecision(this.mode);

    // Re-render the shown date when the language changes
    this.translocoService.langChanges$
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.pickerValue.update((date) => date?.plus(0) ?? null));
  }

  focus(): void {
    this.dateInput().nativeElement.focus();
  }

  /**
   * Raw text of the date input. The text decides the precision: if it fits the input format of
   * another allowed precision, the datepicker switches to it. This cannot rely on `dateInput`
   * of the material input, which is not emitted while the parsed value stays null.
   */
  protected onDateInputChanged(inputText: string): void {
    const detected = resolvePrecisionFromText(
      inputText,
      this.mode(),
      this.allowed(),
      (precision) => this.parseStrict(inputText, precision) !== null,
    );

    if (detected && detected !== this.mode()) {
      this.mode.set(detected); // before committing, so the new precision is serialized
      const date = this.parseStrict(inputText, detected);
      if (date) {
        const normalized = this.normalize(date);
        this.pickerValue.set(normalized);
        this.commit(normalized);
      }
    }

    const parsed = this.dateAdapter.parse(inputText, this.formats.parse.dateInput);
    this.hasParseError.set(!!inputText && !parsed?.isValid);
  }

  /**
   * Parses text strictly with the input format of a precision, which depends on the language.
   * `dateAdapter.parse` is not suitable: it accepts ISO 8601 first, so "2026" is a valid date
   * in every precision and the text would never tell the precisions apart.
   */
  private parseStrict(text: string, precision: DatepickerPrecision): DateTime | null {
    const parsed = DateTime.fromFormat(text, this.formats.formatFor(precision), {
      zone: "utc",
      locale: this.translocoService.getActiveLang(),
    });
    return parsed.isValid ? parsed : null;
  }

  /** Typed text or a pick in the day view. */
  protected onDateInput(event: MatDatepickerInputEvent<DateTime>): void {
    const date = event.value;
    this.commit(date?.isValid ? this.normalize(date) : null);
  }

  /** Year and month views: take the value and close, the calendar would continue to the next view. */
  protected onUnitSelected(
    unit: DateTime,
    precision: "year" | "month",
    picker: MatDatepicker<DateTime>,
  ): void {
    if (this.mode() !== precision) return;
    this.pick(this.normalize(unit));
    picker.close();
  }

  protected onTimeInput(timeText: string): void {
    this.time.set(timeText);
    const date = this.parsed();
    if (date) this.commit(this.normalize(date));
  }

  protected onPrecisionChange(precision: DatepickerPrecision): void {
    if (precision === this.mode() || !this.allowed().includes(precision)) return;
    const date = this.parsed();
    this.mode.set(precision); // before commit, so serialization uses the new mode
    if (date) {
      const converted = this.normalize(date);
      this.pickerValue.set(converted);
      this.commit(converted);
    }
  }

  private normalize(date: DateTime): DateTime {
    return applyPrecision(date, this.mode(), this.time());
  }

  /** Sets value and display explicitly, the picker closes without a dateInput event. */
  private pick(date: DateTime): void {
    this.pickerValue.set(date);
    this.hasParseError.set(!date.isValid);
    this.commit(date);
  }

  private commit(date: DateTime | null): void {
    const serialized = date ? serializeValue(date, this.mode()) : null;
    this.lastEmitted = serialized;
    this.value.set(serialized);
  }
}

/**
 * Error state of the host form field, plus an error while the typed text cannot be parsed.
 */
export class DatepickerErrorStateMatcher implements ErrorStateMatcher {
  private readonly defaultErrorStateMatcher = inject(ErrorStateMatcher);

  constructor(
    private readonly hasParseError: Signal<boolean>,
    private readonly formField: Signal<FieldState<unknown>>,
  ) {}

  isErrorState(control: FormControl | null, formObj: FormGroupDirective | NgForm | null): boolean {
    return this.defaultErrorStateMatcher.isErrorState(control, formObj);
  }

  isSignalErrorState(_field: Field<unknown> | null): boolean {
    const formFieldState = this.defaultErrorStateMatcher.isSignalErrorState
      ? this.defaultErrorStateMatcher.isSignalErrorState(() => this.formField())
      : false;
    return formFieldState || this.hasParseError();
  }
}

/**
 * Component-local date formats: the input format depends on the current precision.
 * The values are read lazily through getters, so changes of precision and language apply immediately.
 */
export class PrecisionDateFormats implements MatDateFormats {
  private readonly translocoService = inject(TranslocoService);
  private precision: Signal<DatepickerPrecision> = signal<DatepickerPrecision>("day");

  constructor(private readonly base: MatDateFormats) {}

  /**
   * Binds the precision the formats should follow.
   * @param precision Signal with the current precision.
   */
  bindPrecision(precision: Signal<DatepickerPrecision>): void {
    this.precision = precision;
  }

  get parse() {
    const dateInput = this.override(this.precision());
    return dateInput ? { dateInput } : this.base.parse;
  }

  get display() {
    const dateInput = this.override(this.precision());
    return dateInput ? { ...this.base.display, dateInput } : this.base.display;
  }

  /**
   * Input format of a precision in the active language. Day and datetime share the date format.
   * @param precision Precision to get the input format for.
   * @returns The input format.
   */
  formatFor(precision: DatepickerPrecision): string {
    return this.override(precision) ?? this.base.parse.dateInput;
  }

  /**
   * Overrides the base format for year and month, null means "use the base format".
   * @param precision Precision to get the override for.
   * @returns The input format or null.
   */
  private override(precision: DatepickerPrecision): string | null {
    switch (precision) {
      case "year":
        return "yyyy";
      case "month":
        return this.translocoService.getActiveLang() === "en" ? "MM/yyyy" : "MM.yyyy";
      default:
        return null;
    }
  }
}
