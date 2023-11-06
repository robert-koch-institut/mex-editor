import { FormlyFieldConfig } from '@ngx-formly/core';
import * as _ from 'lodash-es';

export class FormlyFieldConfigOrderer {
  private readonly configTypeOrder: Record<string, number> = {
    array: 900,
    object: 1000,
  };
  private readonly configKeyOrder: Record<string, number> = {
    identifier: -1,
    language: 200,
  };
  private getFieldGroupSortOrderByLabelOrKey(config: FormlyFieldConfig) {
    const labelOrKey =
      config.props?.label && _.isString(config.props.label) && config.props.label.length >= 1
        ? config.props.label
        : config.key && _.isString(config.key) && config.key.length >= 1
        ? config.key
        : undefined;
    return labelOrKey ? labelOrKey.charCodeAt(0) : 0;
  }

  getOrder(config: FormlyFieldConfig) {
    if (config.key && _.isString(config.key) && config.key in this.configKeyOrder) {
      return this.configKeyOrder[config.key];
    }
    if (config.type && _.isString(config.type) && config.type in this.configTypeOrder) {
      const typeSort = this.configTypeOrder[config.type];
      return typeSort + this.getFieldGroupSortOrderByLabelOrKey(config);
    }

    return this.getFieldGroupSortOrderByLabelOrKey(config);
  }

  order(configs: FormlyFieldConfig[]) {
    return _.orderBy(configs, (x) => this.getOrder(x));
  }
}
