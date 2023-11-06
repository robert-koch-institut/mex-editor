import {
  AfterViewInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnDestroy,
  TemplateRef,
  Type,
  ViewChild,
  ViewEncapsulation,
} from '@angular/core';
import { FormlyFieldConfig, FieldTypeConfig, FormlyConfig, ɵobserve } from '@ngx-formly/core';
import { FieldType } from '@ngx-formly/material';
import { FormlyFieldProps } from '@ngx-formly/material/form-field';

interface DatetTimeProps extends FormlyFieldProps {
  dateTimeOptions: {
    minDate: Date | null;
    maxDate: Date | null;
    showSeconds: boolean;
    showSpinners: boolean;
    stepHour: number;
    stepMinute: number;
    stepSecond: number;
    enableMeridian: boolean;
    disableMinute: boolean;
    opened: boolean;
  };
}

export interface FormlyEntityLookupFieldConfig extends FormlyFieldConfig<DatetTimeProps> {
  type: 'datetime' | Type<DateTimeFormlyFieldTypeComponent>;
}

@Component({
  selector: 'app-date-time-formly-field-type',
  templateUrl: './date-time-formly-field-type.component.html',
  styleUrls: ['./date-time-formly-field-type.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class DateTimeFormlyFieldTypeComponent
  extends FieldType<FieldTypeConfig<DatetTimeProps>>
  implements AfterViewInit, OnDestroy
{
  override defaultOptions = {
    props: {
      dateTimeOptions: {
        minDate: null,
        maxDate: null,
        showSeconds: true,
        showSpinners: true,
        stepHour: 1,
        stepMinute: 1,
        stepSecond: 1,
        enableMeridian: false,
        disableMinute: false,
        opened: false,
      },
    },
  };

  @ViewChild('datepickerToggle', { static: true })
  datepickerToggle!: TemplateRef<unknown>;

  private fieldErrorsObserver!: ReturnType<typeof ɵobserve>;

  constructor(private config: FormlyConfig, private cdRef: ChangeDetectorRef) {
    super();
  }

  detectChanges() {
    this.options.detectChanges?.(this.field);
  }

  ngAfterViewInit() {
    this.props.suffix = this.datepickerToggle;
    ɵobserve<boolean>(this.field, ['props', 'datepickerOptions', 'opened'], () => {
      this.cdRef.detectChanges();
    });

    // temporary fix for https://github.com/angular/components/issues/16761
    if (this.config.getValidatorMessage('matDatetimePickerParse')) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      this.fieldErrorsObserver = ɵobserve<any>(this.field, ['formControl', 'errors'], ({ currentValue }) => {
        if (currentValue && currentValue.required && currentValue.matDatepickerParse) {
          const errors = Object.keys(currentValue)
            .sort((prop) => (prop === 'matDatetimePickerParse' ? -1 : 0))
            .reduce((errors, prop) => ({ ...errors, [prop]: currentValue[prop] }), {});

          this.fieldErrorsObserver?.setValue(errors);
        }
      });
    }
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    this.fieldErrorsObserver?.unsubscribe();
  }
}
