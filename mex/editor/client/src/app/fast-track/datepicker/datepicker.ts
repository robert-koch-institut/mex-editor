import type { Signal } from "@angular/core";
import { computed, ElementRef, linkedSignal, provideAppInitializer, signal } from "@angular/core";
import { Component, inject, input, model, output, viewChild } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import type { FormControl, FormGroupDirective, NgForm } from "@angular/forms";
import type { Field, FieldState, FormValueControl } from "@angular/forms/signals";
import { form, FormField } from "@angular/forms/signals";
import { MatButtonModule } from "@angular/material/button";
import { MatButtonToggleModule } from "@angular/material/button-toggle";
import type { MatDateFormats } from "@angular/material/core";
import { ErrorStateMatcher } from "@angular/material/core";
import { DateAdapter } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import type { MatDatepicker, MatDatepickerInputEvent } from "@angular/material/datepicker";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatIcon, MatIconRegistry } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatMenuModule } from "@angular/material/menu";
import { MatFormField, MatHint, MatPrefix, MatSuffix } from "@angular/material/select";
import { DomSanitizer } from "@angular/platform-browser";
import { TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";

import {
  yearMonthDayPattern,
  yearMonthDayTimePattern,
  yearMonthPattern,
  yearPattern,
} from "../../shared/models/generated/shared";

// Gemeinsamer Kalenderrahmen (Ringe oben, Kopfleiste, Körper als Aussparung)
const FRAME =
  "M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V9h14v11z";

const svg = (...paths: string[]): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">${paths
    .map((d) => `<path d="${d}"/>`)
    .join("")}</svg>`;
/**
 * Icons for datepicker precisions.
 */
export const PRECISION_ICONS = {
  year: svg(
    FRAME,
    "M6.5 10.5h2v2h-2zM9.5 10.5h2v2h-2zM12.5 10.5h2v2h-2zM15.5 10.5h2v2h-2z" +
      "M6.5 13.5h2v2h-2zM9.5 13.5h2v2h-2zM12.5 13.5h2v2h-2zM15.5 13.5h2v2h-2z" +
      "M6.5 16.5h2v2h-2zM9.5 16.5h2v2h-2zM12.5 16.5h2v2h-2zM15.5 16.5h2v2h-2z",
  ),
  month: svg(
    FRAME,
    "M7 11h2v2H7zM11 11h2v2h-2zM15 11h2v2h-2zM7 15h2v2H7zM11 15h2v2h-2zM15 15h2v2h-2z",
  ),
  day: svg(FRAME, "M7 12h5v5H7z"),
  datetime: svg(
    "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16z",
    "M11 7h1.5v5.2l3.6 2.1-.75 1.25L11 13z",
  ),
} as const;

/**
 * AppInitilizer for the Datepicker.
 */
export const datepickerAppInitializer = provideAppInitializer(() => {
  const iconRegistry = inject(MatIconRegistry);
  const sanitizer = inject(DomSanitizer);

  // im Konstruktor
  for (const [name, svgCode] of Object.entries(PRECISION_ICONS)) {
    iconRegistry.addSvgIconLiteral(`precision-${name}`, sanitizer.bypassSecurityTrustHtml(svgCode));
  }
});

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
  const parsed = DateTime.fromISO(value, { zone: "utc" });
  return parsed.isValid ? parsed : null;
}

function serializeValue(date: DateTime, precision: DatepickerPrecision): string {
  const utc = date.toUTC();
  switch (precision) {
    case "year":
      return utc.toFormat("yyyy");
    case "month":
      return utc.toFormat("yyyy-MM");
    case "day":
      return utc.toFormat("yyyy-MM-dd");
    case "datetime":
      // ANNAHME: Format entspricht yearMonthDayTimePattern, bitte prüfen
      return utc.toFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
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
    protected readonly formField: Signal<FieldState<unknown>>,
  ) {}

  isErrorState(_control: FormControl | null, _form: FormGroupDirective | NgForm | null): boolean {
    return this.defaultErrorStateMatcher.isErrorState(_control, _form);
  }
  isSignalErrorState(_field: Field<unknown> | null): boolean {
    const formFieldState = this.defaultErrorStateMatcher.isSignalErrorState
      ? this.defaultErrorStateMatcher.isSignalErrorState(() => this.formField())
      : false;
    return formFieldState || this.hasParseError();
  }
}

const ALL_PRECISIONS: readonly DatepickerPrecision[] = ["year", "month", "day", "datetime"];

@Component({
  selector: "mex-datepicker",
  imports: [
    FormField,
    MatButtonModule,
    MatButtonToggleModule,
    MatDatepickerModule,
    MatFormField,
    MatHint,
    MatIcon,
    MatInput,
    MatMenuModule,
    MatPrefix,
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

  readonly allowedPrecisions = input<readonly DatepickerPrecision[]>(ALL_PRECISIONS);
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

  private readonly parsed = computed(() => parseValue(this.value()));

  private lastEmitted: string | null = null;
  protected readonly pickerValue = linkedSignal<string | null, DateTime | null>({
    source: this.value,
    computation: (value, previous) =>
      previous && value === this.lastEmitted ? previous.value : parseValue(value),
  });

  /** Interner DateTime-Wert als Signal-Form, damit der ErrorStateMatcher ein Field bekommt. */
  protected readonly dateForm = form(this.pickerValue);

  /** Zeitfeld (HH:mm). Bleibt erhalten, wenn noch kein Datum gesetzt ist. */
  protected readonly time = linkedSignal<DateTime | null, string>({
    source: this.parsed,
    computation: (date) => date?.toFormat("HH:mm") ?? "",
  });

  protected readonly hasParseError = signal(false);

  protected readonly dateInput = viewChild.required("dateInput", {
    read: ElementRef<HTMLInputElement>,
  }) as Signal<ElementRef<HTMLInputElement>>;

  protected readonly customErrorMatcher = new DatepickerErrorStateMatcher(
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
    if (date) {
      const converted = this.applyMode(date);
      this.pickerValue.set(converted);
      this.commit(converted);
    }
  }

  private pick(date: DateTime) {
    this.pickerValue.set(date);
    this.hasParseError.set(!date.isValid);
    this.commit(date);
  }

  private applyMode(date: DateTime): DateTime {
    switch (this.mode()) {
      case "year":
        return DateTime.utc(date.year);
      case "month":
        return DateTime.utc(date.year, date.month);
      case "day":
        return DateTime.utc(date.year, date.month, date.day);
      case "datetime": {
        const match = /^(\d{2}):(\d{2})/.exec(this.time());
        return DateTime.utc(
          date.year,
          date.month,
          date.day,
          match ? Number(match[1]) : 0,
          match ? Number(match[2]) : 0,
        );
      }
    }
  }

  private commit(date: DateTime | null) {
    const serialized = date ? serializeValue(date, this.mode()) : null;
    this.lastEmitted = serialized;
    this.value.set(serialized);
  }
}
