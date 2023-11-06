import { Component, Input, OnChanges, Renderer2, SimpleChanges } from '@angular/core';
import { flatMap, isArray, isBoolean, reduce, sortBy, uniq, find, startsWith } from 'lodash-es';
import { map, Observable, of } from 'rxjs';
import { displayEntityFields } from 'src/app/models/constants';
import { SchemaLoaderService } from 'src/app/services/schema-loader.service';
import { nameOf } from 'src/app/util/name-of';
import { JSONSchema7 } from 'json-schema';
import { SchemaRefHelper } from 'src/app/models/schema-ref-helper';
import { MergedEntity } from 'src/app/models/merged-entity';

interface StringPropertyType {
  type: 'string';
  format?: string | string[];
}

interface IdentityRefPropertyType {
  type: 'identity-ref';
}

interface ObjectPropertyType {
  type: 'object';
  objectType: 'link' | 'text' | 'any';
  propertyDescriptors: PropertyDescriptor[];
}

interface ArrayPropertyType {
  type: 'array';
  itemType: StringPropertyType | IdentityRefPropertyType | ObjectPropertyType | UnknwonPropertyType;
}
interface UnknwonPropertyType {
  type: 'unknown';
  schema: JSONSchema7;
}

interface PropertyDescriptor {
  key: string;
  title?: string;

  propertyType:
    | StringPropertyType
    | ArrayPropertyType
    | IdentityRefPropertyType
    | ObjectPropertyType
    | UnknwonPropertyType;
}

@Component({
  selector: 'app-merged-entity-display',
  templateUrl: './merged-entity-display.component.html',
  styleUrls: ['./merged-entity-display.component.scss'],
})
export class MergedEntityDisplayComponent implements OnChanges {
  @Input() entity!: MergedEntity;
  @Input() hideIcon = false;
  @Input() hideAdditionalProperties = false;
  @Input() selected = false;
  @Input() maxLines?: number = undefined;
  @Input() allowWrap = false;

  @Input() maxArrayItems = 5;

  private entitySchema$?: Observable<JSONSchema7>;
  private readonly defaultTitleProperty: PropertyDescriptor = {
    key: 'stableTargetId',
    title: 'Identifier',
    propertyType: { type: 'string' },
  };

  titleProperty$: Observable<PropertyDescriptor> = of(this.defaultTitleProperty);
  additionalProperties$: Observable<PropertyDescriptor[]> = of([]);
  delayLoading = false;

  constructor(private _schemaLoader: SchemaLoaderService, private _renderer: Renderer2) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<MergedEntityDisplayComponent>('entity') in changes) {
      this._updateEntitySchema();
      this._updateTitleProperty();
    }

    if (
      nameOf<MergedEntityDisplayComponent>('entity') in changes ||
      nameOf<MergedEntityDisplayComponent>('hideAdditionalProperties') in changes
    ) {
      this._updateAdditionalProperties();
    }
  }
  private _updateEntitySchema() {
    this.entitySchema$ = this._schemaLoader.loadSchema(this.entity.$type);
  }

  afterPopupOpen() {
    const overlayPane = document.querySelector('.cdk-overlay-pane.more-items-popover');
    if (overlayPane) {
      const style = window.getComputedStyle(overlayPane);
      const verticalOffset = find([style.top, style.bottom], (x) => !startsWith(x, '-'));
      this._renderer.setStyle(overlayPane, 'max-height', `calc(100% - ${verticalOffset ?? '0px'})`);
    }
  }

  private _updateTitleProperty() {
    this.titleProperty$ = this.entitySchema$
      ? this.entitySchema$.pipe(
          map((schema) => {
            const propertyKey = displayEntityFields[this.entity.$type].title;
            if (schema.properties && propertyKey in schema.properties) {
              const schemaProp = schema.properties[propertyKey];
              if (!isBoolean(schemaProp)) {
                return {
                  key: propertyKey,
                  title: schemaProp.title,
                  propertyType: this._createPropertyType(schemaProp),
                };
              }
            }
            return this.defaultTitleProperty;
          })
        )
      : of(this.defaultTitleProperty);
  }

  private _updateAdditionalProperties() {
    const fieldNames = displayEntityFields[this.entity.$type].additionalFields;
    if (this.hideAdditionalProperties || !this.entitySchema$ || !fieldNames) {
      this.additionalProperties$ = of([]);
    } else {
      this.additionalProperties$ = this.entitySchema$.pipe(
        map((x) => {
          const properties = reduce(
            x.properties,
            (prev, prop, key) => {
              if (fieldNames.includes(key) && !isBoolean(prop)) {
                const propertyType = this._createPropertyType(prop);
                prev.push({ key, title: prop.title, propertyType });
              }

              return prev;
            },
            [] as PropertyDescriptor[]
          );
          return sortBy(properties, (x) => fieldNames.indexOf(x.key));
        })
      );
    }
  }

  private refHelper = new SchemaRefHelper();
  private _createPropertyType(
    prop: JSONSchema7
  ): StringPropertyType | ArrayPropertyType | IdentityRefPropertyType | ObjectPropertyType | UnknwonPropertyType {
    if (prop.type === 'string') {
      const anyOfProp = ['anyOf', 'oneOf'].find((x) => x in prop) as keyof JSONSchema7 | undefined;

      if (anyOfProp) {
        const innerProp = prop[anyOfProp] as JSONSchema7[];
        return {
          type: 'string',
          format: uniq(
            flatMap(
              innerProp.map((x) => {
                const innerType = this._createPropertyType(x);
                return innerType.type === 'string' ? innerType.format ?? 'transient' : 'transient';
              })
            )
          ),
        };
      }

      return { type: 'string', format: prop.format };
    }

    if (prop.enum && !isBoolean(prop.enum)) {
      return { type: 'string', format: 'transient' };
    }

    if (prop.type === 'array' && prop.items && !isBoolean(prop.items) && !isArray(prop.items)) {
      const itemType = this._createPropertyType(prop.items);
      if (itemType.type !== 'array') {
        return { type: 'array', itemType };
      }
    }

    if (prop.type === 'object' && prop.properties) {
      const objectType = (['text', 'link'] as const).find((x) => x === prop.title?.toLowerCase());
      return {
        type: 'object',
        objectType: objectType ?? 'any',
        propertyDescriptors: reduce(
          prop.properties,
          (prev, curr, key) => {
            if (!isBoolean(curr)) {
              prev.push({
                key,
                title: curr.title,
                propertyType: this._createPropertyType(curr),
              });
            }
            return prev;
          },
          [] as PropertyDescriptor[]
        ),
      };
    }

    if (prop.$ref) {
      if (this.refHelper.isEntityRefDefType(prop.$ref) || this.refHelper.isEntityRefTypesDef(prop.$ref)) {
        return { type: 'identity-ref' };
      }
    }

    return { type: 'unknown', schema: prop };
  }
}
