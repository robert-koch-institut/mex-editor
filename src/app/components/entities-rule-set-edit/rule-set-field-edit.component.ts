import { Directive, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormlyFieldConfig, FormlyFormOptions } from '@ngx-formly/core';
import * as _ from 'lodash-es';
import { EntityRuleSet, NewEntityRuleSet, ValueRuleSet } from 'src/app/models/entity-rule-set';
import {
  FormlyFieldConfigBuilderService,
  FormlyProps,
  ValueJsonSchema,
} from 'src/app/services/formly-field-config-builder.service';
import { nameOf } from 'src/app/util/name-of';

@Directive()
export abstract class RuleSetFieldEditComponent implements OnChanges {
  @Input() key?: string;
  @Input() ruleSet?: EntityRuleSet | NewEntityRuleSet;
  @Input() schema?: ValueJsonSchema;
  @Input() showKey = true;

  @Output() ruleSetChanged = new EventEmitter<ValueRuleSet>();

  formlyField?: FormlyFieldConfig;
  formlyOptions: FormlyFormOptions = {};
  valueRuleSet?: ValueRuleSet | undefined;

  constructor(private _formlyFieldBuilder: FormlyFieldConfigBuilderService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<RuleSetFieldEditComponent>('schema') in changes) {
      this.updateFormlyField();
    }
    if (nameOf<RuleSetFieldEditComponent>('ruleSet') in changes) {
      this.updateValueRuleSet();
    }
  }
  protected updateValueRuleSet() {
    let valueRuleSet = undefined;
    if (this.ruleSet && this.key) {
      const vrs = this.ruleSet[this.key];
      if (!_.isString(vrs)) {
        valueRuleSet = vrs;
      }
    }
    this.valueRuleSet = valueRuleSet;
  }

  protected updateFormlyField() {
    if (!this.schema || _.isBoolean(this.schema)) {
      this.formlyField = undefined;
    } else {
      this.formlyField = this.buildFormlyFieldConfig(this.schema);
    }
  }

  protected getDefaultProps(field: FormlyFieldConfig): FormlyProps {
    if (field.type && _.isString(field.type) && ['array', 'object'].includes(field.type)) {
      return { hideLabel: true, hideDescription: true };
    }

    return {};
  }

  protected buildFormlyFieldConfig(schema: ValueJsonSchema): FormlyFieldConfig {
    const config = this._formlyFieldBuilder.build(schema, (field) => this.getDefaultProps(field));
    return this._ensureUpdateOnBlur(config);
  }

  private _ensureUpdateOnBlur(config: FormlyFieldConfig): FormlyFieldConfig {
    config.modelOptions = { updateOn: 'blur' };
    if (config.fieldGroup) {
      config.fieldGroup.forEach((x) => this._ensureUpdateOnBlur(x));
    }
    return config;
  }
}
