import { Component, OnInit, Type } from '@angular/core';
import { FieldWrapper, FormlyFieldConfig, FormlyFieldProps } from '@ngx-formly/core';
import * as _ from 'lodash-es';
import { map, Observable, of } from 'rxjs';
import { ValueRuleSet } from 'src/app/models/entity-rule-set';

export interface BlockValueFormlyFieldWrapperProps extends FormlyFieldProps {
  blockValueWrapperOptions: {
    valueRuleSet$: Observable<ValueRuleSet | undefined>;
    onValueRuleSetChanged: (valueRuleSet: ValueRuleSet) => void;
  };
}

export interface BlockValueFormlyFieldWrapperConfig extends FormlyFieldConfig<BlockValueFormlyFieldWrapperProps> {
  type: 'block-value-formly-field-wrapper' | Type<BlockValueFormlyFieldWrapperComponent>;
}

@Component({
  selector: 'app-block-value-formly-field-wrapper',
  templateUrl: './block-value-formly-field-wrapper.component.html',
  styleUrls: ['./block-value-formly-field-wrapper.component.scss'],
})
export class BlockValueFormlyFieldWrapperComponent
  extends FieldWrapper<BlockValueFormlyFieldWrapperConfig>
  implements OnInit
{
  isValueBlocked$: Observable<{
    valueRuleSet: ValueRuleSet;
    isValueBlocked: boolean;
  }> = of({ valueRuleSet: {}, isValueBlocked: false });

  ngOnInit(): void {
    this.isValueBlocked$ = this.props.blockValueWrapperOptions.valueRuleSet$.pipe(
      map((x) => {
        return {
          valueRuleSet: x ?? {},
          isValueBlocked: x?.blockValue ? _.some(x.blockValue, (x) => _.isEqual(x, this.formControl.value)) : false,
        };
      })
    );
  }

  blockValue(valueRuleSet: ValueRuleSet) {
    const update: ValueRuleSet = {
      ...valueRuleSet,
      blockValue: _.uniqWith([...(valueRuleSet?.blockValue ?? []), this.formControl.value], _.isEqual),
    };
    this.props.blockValueWrapperOptions.onValueRuleSetChanged(update);
  }

  unblockValue(valueRuleSet: ValueRuleSet) {
    if (valueRuleSet.blockValue) {
      const update: ValueRuleSet = {
        ...valueRuleSet,
        blockValue: valueRuleSet.blockValue.filter((x) => !_.isEqual(x, this.formControl.value)),
      };
      this.props.blockValueWrapperOptions.onValueRuleSetChanged(update);
    }
  }
}
