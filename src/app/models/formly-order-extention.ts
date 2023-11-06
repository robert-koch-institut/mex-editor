import { FormlyExtension } from '@ngx-formly/core';
import { FormlyFieldConfigOrderer } from './formly-field-config-orderer';

const orderer = new FormlyFieldConfigOrderer();
export const orderFieldGroupExtension: FormlyExtension = {
  prePopulate(field): void {
    if ((field.type === 'array' || field.type === 'object') && field.fieldGroup) {
      field.fieldGroup = orderer.order(field.fieldGroup);
    }
  },
};
