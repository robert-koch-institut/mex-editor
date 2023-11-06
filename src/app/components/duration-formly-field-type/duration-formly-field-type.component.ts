import { Component, Type } from '@angular/core';
import { FieldTypeConfig, FormlyFieldConfig } from '@ngx-formly/core';
import { FieldType, FormlyFieldProps } from '@ngx-formly/material/form-field';
import { DurationUnit, DEFAULT_DURATION_UNITS } from '../duration-control/duration-control.component';

interface DurationFormlyFieldTypeProps extends FormlyFieldProps {
  durationOptions?: Partial<{
    units: DurationUnit[];
  }>;
}

export interface DurationFormlyFieldTypeConfig extends FormlyFieldConfig<DurationFormlyFieldTypeProps> {
  type: 'duration' | Type<DurationFormlyFieldTypeComponent>;
}

@Component({
  selector: 'app-duration-formly-field-type',
  templateUrl: './duration-formly-field-type.component.html',
  styleUrls: ['./duration-formly-field-type.component.scss'],
})
//
export class DurationFormlyFieldTypeComponent extends FieldType<FieldTypeConfig<DurationFormlyFieldTypeProps>> {
  override defaultOptions?: Partial<FieldTypeConfig<DurationFormlyFieldTypeProps>> | undefined = {
    props: {
      durationOptions: {
        units: DEFAULT_DURATION_UNITS,
      },
    },
  };

  get placeholderLabel() {
    const text = this.props.placeholder || this.props.label;
    return this.props.required ? text + ' *' : text;
  }
}
