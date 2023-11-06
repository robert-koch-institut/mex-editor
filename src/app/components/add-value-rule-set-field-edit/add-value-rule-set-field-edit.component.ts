import { Component, OnChanges, SimpleChanges } from '@angular/core';
import { JSONSchema7 } from 'json-schema';
import { cloneDeep, isArray, isNil, isUndefined } from 'lodash-es';
import { nameOf } from 'src/app/util/name-of';
import { RuleSetFieldEditComponent } from '../entities-rule-set-edit/rule-set-field-edit.component';
import { SchemaRefHelper } from 'src/app/models/schema-ref-helper';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: '[add-value-rule-set-field-edit]',
  templateUrl: './add-value-rule-set-field-edit.component.html',
  styleUrls: ['./add-value-rule-set-field-edit.component.scss'],
})
export class AddValueRuleSetFieldEditComponent extends RuleSetFieldEditComponent implements OnChanges {
  model: unknown = undefined;

  override ngOnChanges(changes: SimpleChanges): void {
    super.ngOnChanges(changes);

    if (
      nameOf<AddValueRuleSetFieldEditComponent>('schema') in changes ||
      nameOf<AddValueRuleSetFieldEditComponent>('ruleSet') in changes
    ) {
      this.updateModel();
    }
  }

  onModelChanged(change?: { value?: unknown }) {
    if (change && change.value !== undefined) {
      const update = { ...this.valueRuleSet, addValue: change.value };
      this.ruleSetChanged.emit(update);
    }
  }

  private updateModel() {
    if (this.schema) {
      this.model = {
        value: isNil(this.valueRuleSet?.addValue)
          ? this.getDefaultValue(this.schema.properties.value)
          : cloneDeep(this.valueRuleSet?.addValue),
      };
    } else {
      this.model = undefined;
    }
    if (this.formlyOptions.resetModel) {
      this.formlyOptions.resetModel();
    }
  }

  private getDefaultValue(valueSchema: JSONSchema7): unknown {
    if ('default' in valueSchema) {
      return cloneDeep(valueSchema.default);
    }

    if ('$ref' in valueSchema && valueSchema.$ref) {
      const refHelper = new SchemaRefHelper();
      if (refHelper.isEntityRefDefType(valueSchema.$ref)) {
        return undefined;
      }
    }

    if (isUndefined(valueSchema.type) || isArray(valueSchema.type))
      throw new Error(
        `The type '${
          valueSchema.type
        }' can't be handled because it's undefined or an array (only single values can be handled). Schema source: ${JSON.stringify(
          valueSchema
        )}.`
      );

    switch (valueSchema.type) {
      case 'array':
        return [];
      case 'object':
        return {};
      case 'number':
      case 'integer':
        return 0;
      case 'boolean':
        return false;
      case 'null':
        return null;
      default:
        return undefined;
    }
  }
}
