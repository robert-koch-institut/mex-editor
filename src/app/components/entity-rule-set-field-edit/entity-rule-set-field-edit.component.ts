import { Component, Inject, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Entity } from 'src/app/models/entity';
import { ValueRuleSet } from 'src/app/models/entity-rule-set';
import { FieldArrayTypeConfig, FormlyFieldConfig } from '@ngx-formly/core';
import { nameOf } from 'src/app/util/name-of';
import {
  FormlyFieldConfigBuilderService,
  FormlyProps,
  ValueJsonSchema,
} from 'src/app/services/formly-field-config-builder.service';
import * as _ from 'lodash-es';
import { BehaviorSubject, Observable } from 'rxjs';
import { RuleSetFieldEditComponent } from '../entities-rule-set-edit/rule-set-field-edit.component';
import { BlockValueFormlyFieldWrapperProps } from '../block-value-formly-field-wrapper/block-value-formly-field-wrapper.component';
import { FORMLY_WRAPPER_MAP } from 'src/app/util/create-formly-wrapper-map';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';
import { MergedEntity } from 'src/app/models/merged-entity';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: '[entity-rule-set-field-edit]',
  templateUrl: './entity-rule-set-field-edit.component.html',
  styleUrls: ['./entity-rule-set-field-edit.component.scss'],
})
export class EntityRuleSetFieldEditComponent extends RuleSetFieldEditComponent implements OnChanges {
  @Input() entity?: Entity;
  @Input() primarySource$?: Observable<MergedEntity | undefined>;

  private valueRuleSet$ = new BehaviorSubject<ValueRuleSet | undefined>(undefined);
  model: unknown = undefined;
  isPrimarySourceBlocked = false;

  constructor(
    formlyBuilder: FormlyFieldConfigBuilderService,
    private _entityLoader: EntityLoaderService,
    @Inject(FORMLY_WRAPPER_MAP)
    private _defaultFormlyWrappers: Map<string, string[]>
  ) {
    super(formlyBuilder);
  }

  override ngOnChanges(changes: SimpleChanges): void {
    super.ngOnChanges(changes);

    if (
      nameOf<EntityRuleSetFieldEditComponent>('entity') in changes ||
      nameOf<EntityRuleSetFieldEditComponent>('key') in changes
    ) {
      this.updateModel();
    }

    if (
      nameOf<EntityRuleSetFieldEditComponent>('entity') in changes ||
      nameOf<EntityRuleSetFieldEditComponent>('ruleSet') in changes ||
      nameOf<EntityRuleSetFieldEditComponent>('key') in changes
    ) {
      this.updateIsPrimarySourceBlocked();
    }
  }

  protected override updateValueRuleSet(): void {
    super.updateValueRuleSet();
    this.valueRuleSet$.next(this.valueRuleSet);
  }

  updateIsPrimarySourceBlocked() {
    this.isPrimarySourceBlocked =
      this.entity && this.valueRuleSet && this.valueRuleSet.blockPrimarySource
        ? this.valueRuleSet.blockPrimarySource.includes(this.entity.hadPrimarySource)
        : false;
  }

  updateModel() {
    if (this.entity && this.key && this.key in this.entity) {
      this.model = { value: this.entity[this.key] };
    } else {
      this.model = undefined;
    }

    if (this.formlyOptions.resetModel) {
      this.formlyOptions.resetModel(this.model);
    }
  }

  protected override getDefaultProps(field: FormlyFieldConfig): FormlyProps {
    const defaultProps = super.getDefaultProps(field);
    defaultProps.readonly = true;
    if (field.props?.options && _.isArray(field.props.options)) {
      field.props.options = field.props.options.map((o) => {
        o.disabled = true;
        return o;
      });
    }
    return defaultProps;
  }

  protected override buildFormlyFieldConfig(schema: ValueJsonSchema): FormlyFieldConfig {
    const fieldConfig = super.buildFormlyFieldConfig(schema);
    const valuePropConfig = _.first(fieldConfig.fieldGroup);
    if (valuePropConfig) {
      if (valuePropConfig.type === 'array') {
        const arrayValueField = valuePropConfig as FieldArrayTypeConfig;
        if (arrayValueField.fieldArray !== undefined) {
          if (_.isFunction(arrayValueField.fieldArray)) {
            const original = arrayValueField.fieldArray;
            arrayValueField.fieldArray = (f) => {
              const origianlValue = original(f);
              this.wrapFieldInValueBlockWrapper(origianlValue);
              return origianlValue;
            };
          } else {
            this.wrapFieldInValueBlockWrapper(arrayValueField.fieldArray);
          }
        }
      } else {
        this.wrapFieldInValueBlockWrapper(valuePropConfig);
      }
    }

    return fieldConfig;
  }

  private wrapFieldInValueBlockWrapper(field: FormlyFieldConfig) {
    const blockValueWrapperProps: BlockValueFormlyFieldWrapperProps = {
      blockValueWrapperOptions: {
        valueRuleSet$: this.valueRuleSet$.asObservable(),
        onValueRuleSetChanged: (x) => this.ruleSetChanged.emit(x),
      },
    };

    const existingWrappers = field.wrappers || this.getDefaultWrapper(field);
    field.wrappers = ['block-value-wrapper', ...existingWrappers];
    field.props = { ...field.props, ...blockValueWrapperProps };
  }

  private getDefaultWrapper(field: FormlyFieldConfig): string[] {
    if (field.type && _.isString(field.type) && this._defaultFormlyWrappers.has(field.type)) {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      return this._defaultFormlyWrappers.get(field.type)!;
    }
    return [];
  }

  blockPrimarySource() {
    if (this.entity) {
      const update = this.valueRuleSet ? { ...this.valueRuleSet } : {};
      update.blockPrimarySource = update.blockPrimarySource
        ? _.uniq([...update.blockPrimarySource, this.entity.hadPrimarySource])
        : [this.entity.hadPrimarySource];
      this.ruleSetChanged.emit(update);
    }
  }
  unblockPrimarySource() {
    if (this.entity && this.valueRuleSet && this.valueRuleSet.blockPrimarySource) {
      const unblock = this.entity.hadPrimarySource;
      const update = {
        ...this.ruleSet,
        blockPrimarySource: this.valueRuleSet.blockPrimarySource.filter((x) => x !== unblock),
      };
      this.ruleSetChanged.emit(update);
    }
  }
}
