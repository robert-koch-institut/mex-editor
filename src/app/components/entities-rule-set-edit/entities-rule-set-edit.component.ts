import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewEncapsulation } from '@angular/core';
import * as _ from 'lodash-es';
import { Entity } from 'src/app/models/entity';
import { EntityRuleSet, NewEntityRuleSet, ValueRuleSet } from 'src/app/models/entity-rule-set';
import { nameOf } from 'src/app/util/name-of';
import { JSONSchema7 } from 'json-schema';
import { uneditableEntityFields } from 'src/app/models/constants';
import { log } from 'src/app/util/log-method.decorator';
import { ValueJsonSchema } from 'src/app/services/formly-field-config-builder.service';
import { MergedEntity } from 'src/app/models/merged-entity';
import { Observable, of, shareReplay } from 'rxjs';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';

interface EntityEditField {
  $type: 'entity-edit-field';
  key: string;
  showKey: boolean;
  propertySchema: ValueJsonSchema;
  primarySource$: Observable<MergedEntity | undefined>;

  entity: Entity;
}

interface RuleSetEditField {
  $type: 'rule-set-edit-field';
  key: string;
  showKey: boolean;
  propertySchema: ValueJsonSchema;
}

type EditField = EntityEditField | RuleSetEditField;

@Component({
  selector: 'app-entities-rule-set-edit',
  templateUrl: './entities-rule-set-edit.component.html',
  styleUrls: ['./entities-rule-set-edit.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class EntitiesRuleSetEditComponent implements OnChanges {
  @Input() entities?: Entity[];
  @Input() schema?: JSONSchema7 | undefined;
  @Input() ruleSet?: EntityRuleSet | NewEntityRuleSet | undefined;
  @Output() ruleSetChanged = new EventEmitter<EntityRuleSet>();

  fields: EditField[] = [];

  constructor(private _entityLoader: EntityLoaderService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (
      nameOf<EntitiesRuleSetEditComponent>('schema') in changes ||
      nameOf<EntitiesRuleSetEditComponent>('entities') in changes
    ) {
      this.updateFields();
    }
  }

  updateFields() {
    if (this.schema?.properties && this.entities) {
      const entities = this.entities;
      const primarySources = entities.reduce((prev, curr) => {
        prev.set(curr.hadPrimarySource, this._entityLoader.loadMergedEntity(curr.hadPrimarySource).pipe(shareReplay()));
        return prev;
      }, new Map<string, Observable<MergedEntity>>());

      this.fields = _.reduce(
        this.schema.properties,
        (prev, curr, key) => {
          if (!uneditableEntityFields.includes(key) && !_.isBoolean(curr)) {
            const propertySchema = {
              properties: { value: { ...curr, title: curr.title ?? key } },
              $defs: this.schema?.$defs ?? {},
            };

            let showKey = true;
            for (const entity of entities) {
              if (key in entity) {
                prev.push({
                  $type: 'entity-edit-field',
                  key,
                  propertySchema,
                  entity,
                  showKey,
                  primarySource$: primarySources.get(entity.hadPrimarySource) ?? of(undefined),
                });
                showKey = false;
              }
            }

            prev.push({
              $type: 'rule-set-edit-field',
              showKey,
              key,
              propertySchema,
            });
          }

          return prev;
        },
        [] as EditField[]
      );
    } else {
      this.fields = [];
    }
  }

  @log('in')
  onValueRuleSetChanged(key: string, valueRuleSet: ValueRuleSet) {
    const value = this.ruleSet && key in this.ruleSet ? this.ruleSet[key] : undefined;
    const existingValue = _.isString(value) ? undefined : value;
    const ruleSetUpdate = {
      ...this.ruleSet,
      [key]: { ...existingValue, ...valueRuleSet },
    } as EntityRuleSet;
    this.ruleSet = ruleSetUpdate;
    this.ruleSetChanged.emit(ruleSetUpdate);
  }
}
