import { Component, forwardRef, Input } from '@angular/core';
import { FormGroup, FormControl, ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { Duration, formatISODuration } from 'date-fns';
import * as _ from 'lodash-es';

export type DurationUnit = 'years' | 'months' | 'weeks' | 'days' | 'hours' | 'minutes' | 'seconds';

export const DEFAULT_DURATION_UNITS: DurationUnit[] = [
  'years',
  'months',
  'weeks',
  'days',
  'hours',
  'minutes',
  'seconds',
];

const ISO_DURATION_REGEX = /^P(?:(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?|(?:(\d+)W))$/;

export function parseISODuration(duration: string): Duration {
  const match = duration.match(ISO_DURATION_REGEX);
  if (!match) {
    throw new Error(`Invalid duration: ${duration}`);
  }

  return {
    years: Number(match[1]) || 0,
    months: Number(match[2]) || 0,
    days: Number(match[3]) || 0,
    hours: Number(match[4]) || 0,
    minutes: Number(match[5]) || 0,
    seconds: Number(match[6]) || 0,
    weeks: Number(match[7]) || 0,
  };
}

@Component({
  selector: 'app-duration-control',
  templateUrl: './duration-control.component.html',
  styleUrls: ['./duration-control.component.scss'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DurationControlComponent),
      multi: true,
    },
  ],
})
export class DurationControlComponent implements ControlValueAccessor {
  @Input() units?: DurationUnit[] = DEFAULT_DURATION_UNITS;

  unitConfig = {
    years: { label: 'Years' },
    months: { label: 'Months' },
    weeks: { label: 'Weeks' },
    days: { label: 'Days' },
    hours: { label: 'Hours' },
    minutes: { label: 'Minutes' },
    seconds: { label: 'Seconds' },
  };

  duration: Duration = {
    years: 0,
    months: 0,
    weeks: 0,
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  };

  form = new FormGroup({
    years: new FormControl(0),
    months: new FormControl(0),
    weeks: new FormControl(0),
    days: new FormControl(0),
    hours: new FormControl(0),
    minutes: new FormControl(0),
    seconds: new FormControl(0),
  });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onChange: any = _.noop;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onTouch: any = _.noop;

  constructor() {
    this.form.valueChanges.subscribe((value) => {
      const durationStr = formatISODuration({
        years: value.years ?? undefined,
        months: value.months ?? undefined,
        weeks: value.weeks ?? undefined,
        days: value.days ?? undefined,
        hours: value.hours ?? undefined,
        minutes: value.minutes ?? undefined,
        seconds: value.seconds ?? undefined,
      });
      this.onChange(durationStr);
      this.onTouch(durationStr);
    });
  }

  writeValue(value: string) {
    if (value === undefined || value === null) {
      return;
    }

    const duration = parseISODuration(value);
    this.form.setValue({
      years: duration.years ?? null,
      months: duration.months ?? null,
      weeks: duration.weeks ?? null,
      days: duration.days ?? null,
      hours: duration.hours ?? null,
      minutes: duration.minutes ?? null,
      seconds: duration.seconds ?? null,
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  registerOnChange(fn: any) {
    this.onChange = fn;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  registerOnTouched(fn: any) {
    this.onTouch = fn;
  }

  setDisabledState(isDisabled: boolean) {
    isDisabled ? this.form.disable() : this.form.enable();
  }

  trackBy(index: number, unit: DurationUnit) {
    return unit;
  }
}
