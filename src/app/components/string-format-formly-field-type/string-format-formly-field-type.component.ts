import { Component, OnInit, Type } from '@angular/core';
import { FormlyFieldProps, FormlyFieldConfig, FieldType, FieldTypeConfig } from '@ngx-formly/core';
import * as _ from 'lodash-es';

export interface StringFormatFieldGroupMatcher {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  matches: (value: any) => boolean;
  fieldGroupIndex: number;
  label: string;
  priority: number;
}

export interface StringFormatProps extends FormlyFieldProps {
  stringFormatOptions: {
    formatMatchers: StringFormatFieldGroupMatcher[];
  };
}

export interface StringFormatFieldConfig extends FormlyFieldConfig<StringFormatProps> {
  type: 'string-format' | Type<StringFormatFormlyFieldTypeComponent>;
}

@Component({
  selector: 'app-string-format-formly-field-type',
  templateUrl: './string-format-formly-field-type.component.html',
  styleUrls: ['./string-format-formly-field-type.component.scss'],
})
export class StringFormatFormlyFieldTypeComponent
  extends FieldType<FieldTypeConfig<StringFormatProps>>
  implements OnInit
{
  private _selectedMatcher?: StringFormatFieldGroupMatcher;
  get selectedMatcher() {
    return this._selectedMatcher;
  }
  set selectedMatcher(value: StringFormatFieldGroupMatcher | undefined) {
    if (this._selectedMatcher !== value) {
      this._selectedMatcher = value;

      const newField =
        this.field.fieldGroup && this._selectedMatcher
          ? this.field.fieldGroup[this._selectedMatcher.fieldGroupIndex]
          : undefined;
      // TODO: wenn newField die aktuelle value nicht passt (matches(value) === false) dann leeren
      this.selectedField = newField;
    }
  }

  selectedField?: FormlyFieldConfig;

  // @logMore<StringFormatFormlyFieldTypeComponent>('in', x => ({ field: x.field, model: x.model, form: x.form, key: x.key, formControl: x.formControl }))
  ngOnInit(): void {
    this.selectedMatcher = _.find(
      _.orderBy(this.props.stringFormatOptions.formatMatchers, (x) => x.priority),
      (x) => {
        if (this.field.fieldGroup && x.fieldGroupIndex < this.field.fieldGroup.length) {
          return x.matches(this.field.fieldGroup[x.fieldGroupIndex].formControl?.value);
        }
        return false;
      }
    );
  }
}
