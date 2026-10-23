import type { Signal } from "@angular/core";
import { computed, ElementRef, linkedSignal, signal } from "@angular/core";
import { Component, inject, input, model, output, viewChild } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import type { Field, FieldState, FormValueControl } from "@angular/forms/signals";
import { FormField } from "@angular/forms/signals";
import { MatButtonToggleModule } from "@angular/material/button-toggle";
import type { MatDateFormats } from "@angular/material/core";
import { ErrorStateMatcher } from "@angular/material/core";
import { DateAdapter } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import type { MatDatepicker, MatDatepickerInputEvent } from "@angular/material/datepicker";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatHint, MatSuffix } from "@angular/material/select";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";

import {
  yearMonthDayPattern,
  yearMonthDayTimePattern,
  yearMonthPattern,
  yearPattern,
} from "../../shared/models/generated/shared";

/**
 * Precision for datepicker selection behaviour.
 */
export type DatepickerPrecision = "year" | "month" | "day" | "datetime";

const PRECISION_REGEXES: [DatepickerPrecision, RegExp][] = [
  // Reihenfolge: spezifisch -> unspezifisch
  ["datetime", new RegExp(yearMonthDayTimePattern)],
  ["day", new RegExp(yearMonthDayPattern)],
  ["month", new RegExp(yearMonthPattern)],
  ["year", new RegExp(yearPattern)],
];

function detectPrecision(value: string | null): DatepickerPrecision | null {
  if (!value) return null;
  return PRECISION_REGEXES.find(([, regex]) => regex.test(value))?.[0] ?? null;
}

function parseValue(value: string | null): DateTime | null {
  const precision = detectPrecision(value);
  if (!value || !precision) return null;
  // ANNAHME: Zeitwerte sind UTC, Anzeige/Bearbeitung in lokaler Zeit
  const parsed =
    precision === "datetime"
      ? DateTime.fromISO(value, { zone: "utc" }).toLocal()
      : DateTime.fromISO(value);
  return parsed.isValid ? parsed : null;
}

function serializeValue(date: DateTime, precision: DatepickerPrecision): string {
  switch (precision) {
    case "year":
      return date.toFormat("yyyy");
    case "month":
      return date.toFormat("yyyy-MM");
    case "day":
      return date.toFormat("yyyy-MM-dd");
    case "datetime":
      // ANNAHME: Format entspricht yearMonthDayTimePattern, bitte prüfen
      return date.toUTC().toFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
  }
}

/** Komponentenlokale Date-Formats: Eingabeformat hängt vom aktuellen Modus ab (lazy über Getter). */
class PrecisionDateFormats implements MatDateFormats {
  private translocoService = inject(TranslocoService);

  precision: Signal<DatepickerPrecision> = signal<DatepickerPrecision>("day");

  constructor(private readonly base: MatDateFormats) {}

  get parse() {
    switch (this.precision()) {
      case "year":
        return { dateInput: "yyyy" };
      case "month":
        return { dateInput: this.translocoService.getActiveLang() == "en" ? "MM/yyyy" : "MM.yyyy" };
      default:
        return this.base.parse;
    }
  }

  get display() {
    switch (this.precision()) {
      case "year":
        return { ...this.base.display, dateInput: "yyyy" };
      case "month":
        return {
          ...this.base.display,
          dateInput: this.translocoService.getActiveLang() == "en" ? "MM/yyyy" : "MM.yyyy",
        };
      default:
        return this.base.display;
    }
  }
}

class DatepickerErrorStateMatcher implements ErrorStateMatcher {
  protected defaultErrorStateMatcher = inject(ErrorStateMatcher);

  constructor(
    protected readonly hasParseError: Signal<boolean>,
    // protected readonly formField: Signal<FieldState<unknown>>,
  ) {}

  isErrorState(_control: FormControl | null, _form: FormGroupDirective | NgForm | null): boolean {
    return this.defaultErrorStateMatcher.isErrorState(_control, _form);
  }
  isSignalErrorState(field: Field<unknown> | null): boolean {
    console.log("ERRORSTATE", field, this.formField());
    const defaultState = this.defaultErrorStateMatcher.isSignalErrorState
      ? this.defaultErrorStateMatcher.isSignalErrorState(field)
      : false;
    return defaultState || this.hasParseError();
  }
}

const ALL_PRECISIONS: readonly DatepickerPrecision[] = ["year", "month", "day", "datetime"];

@Component({
  selector: "mex-datepicker",
  imports: [
    MatButtonToggleModule,
    MatDatepickerModule,
    MatFormField,
    MatHint,
    MatInput,
    MatSuffix,
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
 * (YYYY, YYYY-MM, YYYY-MM-DD, Datum+Zeit); der Editiermodus folgt dem Format.
 */
export class Datepicker implements FormValueControl<string | null> {
  protected formats = inject(MAT_DATE_FORMATS) as unknown as PrecisionDateFormats;
  protected hostFormField = inject(FormField);
  protected translocoService = inject(TranslocoService);
  protected dateAdapter = inject(DateAdapter<DateTime>);

  readonly value = model<string | null>(null);
  readonly disabled = input<boolean>(false);
  readonly readonly = input<boolean>(false);
  readonly touch = output<void>();

  readonly minDate = input<DateTime | null>(null);
  readonly maxDate = input<DateTime | null>(null);

  /** Which precisions the user may choose. Defaults to all. */
  readonly allowedPrecisions = input<readonly DatepickerPrecision[]>(ALL_PRECISIONS);
  /** Default precision while no value is set. Falls back to the first allowed one. */
  readonly precision = input<DatepickerPrecision | null>(null);

  protected readonly precisionOptions = ALL_PRECISIONS;

  protected readonly allowed = computed(() => {
    const list = this.allowedPrecisions();
    return list.length ? list : ALL_PRECISIONS; // empty list = no restriction
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
    computation: (source, previous) => {
      // 1. an existing value always determines the mode, even if it is not "allowed",
      //    so that existing data is never silently changed
      const detected = detectPrecision(source.value);
      if (detected) return detected;
      // 2. otherwise: last mode -> default input -> first allowed, as long as it is allowed
      return (
        [previous?.value, source.precision].find((p) => p && source.allowed.includes(p)) ??
        source.allowed[0] ??
        "day"
      );
    },
  });

  protected isAllowed(precision: DatepickerPrecision): boolean {
    return this.allowed().includes(precision);
  }

  protected readonly startView = computed(() =>
    this.mode() === "year" || this.mode() === "month" ? "multi-year" : "month",
  );

  /** Der Wert, den der Value als DateTime repräsentiert (Basis für Zeit-Anteil und Kombination). */
  private readonly parsed = computed(() => parseValue(this.value()));

  /**
   * Wert, der im Datepicker-Input angezeigt wird. Eigene Änderungen (lastEmitted) werden nicht
   * zurückgeschrieben, sonst würde der Text beim Tippen (z. B. bei Teileingaben) überschrieben.
   */
  private lastEmitted: string | null = null;
  protected readonly pickerValue = linkedSignal<string | null, DateTime | null>({
    source: this.value,
    computation: (value, previous) =>
      previous && value === this.lastEmitted ? previous.value : parseValue(value),
  });

  /** Zeitfeld (HH:mm). Bleibt erhalten, wenn noch kein Datum gesetzt ist. */
  protected readonly time = linkedSignal<DateTime | null, string>({
    source: this.parsed,
    computation: (date) => date?.toFormat("HH:mm") ?? "",
  });

  readonly hasParseError = signal(false);

  dateInput = viewChild.required("dateInput", {
    read: ElementRef<HTMLInputElement>,
  }) as Signal<ElementRef<HTMLInputElement>>;

  customErrorMatcher = new DatepickerErrorStateMatcher(
    this.hasParseError,
    this.hostFormField.state,
  );

  constructor() {
    this.formats.precision = this.mode;

    // Anzeige neu formatieren, wenn die Sprache wechselt
    this.translocoService.langChanges$
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.pickerValue.update((x) => (x == null ? null : x.plus(0))));
  }

  focus(): void {
    this.dateInput().nativeElement.focus();
  }

  protected onDateInputChanged(inputText: string) {
    const parsed = this.dateAdapter.parse(inputText, this.formats.parse.dateInput);
    this.hasParseError.set(!!inputText && (parsed == null || !parsed.isValid));
  }

  /** Eingabe oder Auswahl im Datepicker (Tag-Ansicht bzw. getippter Text). */
  protected onDateInput(event: MatDatepickerInputEvent<DateTime>) {
    const date = event.value;
    if (!date?.isValid) {
      this.commit(null);
      return;
    }
    this.commit(this.applyMode(date));
  }

  protected onYearSelected(normalizedYear: DateTime, picker: MatDatepicker<DateTime>) {
    if (this.mode() !== "year") return;
    this.pick(normalizedYear.startOf("year"));
    picker.close();
  }

  protected onMonthSelected(normalizedMonth: DateTime, picker: MatDatepicker<DateTime>) {
    if (this.mode() !== "month") return;
    this.pick(normalizedMonth.startOf("month"));
    picker.close();
  }

  protected onTimeInput(timeText: string) {
    this.time.set(timeText);
    const date = this.parsed();
    if (date) this.commit(this.applyMode(date));
  }

  protected onPrecisionChange(precision: DatepickerPrecision) {
    if (precision === this.mode() || !this.isAllowed(precision)) return;
    const date = this.parsed();
    this.mode.set(precision); // before commit, so serialization uses the new mode
    this.hasParseError.set(false);
    if (date) {
      const converted = this.applyMode(date);
      this.pickerValue.set(converted);
      this.commit(converted);
    }
  }

  /** Setzt Wert und Anzeige explizit (Picker wird ohne dateInput-Event geschlossen). */
  private pick(date: DateTime) {
    this.pickerValue.set(date);
    this.hasParseError.set(false);
    this.commit(date);
  }

  /** Normalisiert das Datum auf die Genauigkeit des Modus. */
  private applyMode(date: DateTime): DateTime {
    switch (this.mode()) {
      case "year":
        return date.startOf("year");
      case "month":
        return date.startOf("month");
      case "day":
        return date.startOf("day");
      case "datetime": {
        const match = /^(\d{2}):(\d{2})/.exec(this.time());
        return date.set({
          hour: match ? Number(match[1]) : 0,
          minute: match ? Number(match[2]) : 0,
          second: 0,
          millisecond: 0,
        });
      }
    }
  }

  private commit(date: DateTime | null) {
    const serialized = date ? serializeValue(date, this.mode()) : null;
    this.lastEmitted = serialized;
    this.value.set(serialized);
  }
}
