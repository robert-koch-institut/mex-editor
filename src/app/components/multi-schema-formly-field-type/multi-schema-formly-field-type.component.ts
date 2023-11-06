import { Component, Type } from '@angular/core';
import { FormlyFieldProps, FormlyFieldConfig, FieldType, FieldTypeConfig } from '@ngx-formly/core';

export interface FormlyLookupFieldConfig extends FormlyFieldConfig<FormlyFieldProps> {
  type: 'multi-schema' | Type<MultiSchemaFormlyFieldTypeComponent>;
}

@Component({
  selector: 'app-multi-schema-formly-field-type',
  templateUrl: './multi-schema-formly-field-type.component.html',
  styleUrls: ['./multi-schema-formly-field-type.component.scss'],
})
export class MultiSchemaFormlyFieldTypeComponent extends FieldType<FieldTypeConfig<FormlyFieldProps>> {}
