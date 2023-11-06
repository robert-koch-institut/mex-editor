import { FormlyFieldConfig, FormlyFieldProps } from '@ngx-formly/core';
import { formatISO } from 'date-fns';
import { JSONSchema7, JSONSchema7Definition } from 'json-schema';
import { EntityType } from '../models/entity-type';
import * as _ from 'lodash-es';
import { FormlyJsonschema } from '@ngx-formly/core/json-schema';
import { StringFormatFieldGroupMatcher } from '../components/string-format-formly-field-type/string-format-formly-field-type.component';
import { SchemaRefHelper } from '../models/schema-ref-helper';
import { Injectable } from '@angular/core';
import { StringFormatMatchers } from '../models/string-format-matcher';

export const StringFormatValues = ['date', 'datetime', 'date-time', 'transient'] as const;
export type StringFormatTuple = typeof StringFormatValues;
export type StringFormat = StringFormatTuple[number];

export interface ValueJsonSchema {
  properties: { value: JSONSchema7 };
  $defs: {
    [key: string]: JSONSchema7Definition;
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type FormlyProps = FormlyFieldProps & {
  [additionalProperties: string]: any;
};

@Injectable({
  providedIn: 'root',
})
export class FormlyFieldConfigBuilderService {
  private readonly _formlyJsonschema = new FormlyJsonschema();
  private readonly _refHelper = new SchemaRefHelper();

  // @log('out')
  build(schema: JSONSchema7, getDefaultProps?: (field: FormlyFieldConfig) => FormlyProps | undefined) {
    return this.createFieldConfig(schema, getDefaultProps);
  }

  private createFieldConfig(
    schema: JSONSchema7,
    getDefaultProps?: (field: FormlyFieldConfig) => FormlyProps | undefined
  ) {
    return this._formlyJsonschema.toFieldConfig(schema, {
      map: (field, source) => {
        const mapped = this.mapSchema(field, source);
        if (getDefaultProps) {
          const defaultProps = getDefaultProps(mapped);
          mapped.props = { ...mapped.props, ...defaultProps };
        }
        return mapped;
      },
    });
  }

  private mapSchema(mappedField: FormlyFieldConfig, mapSource: JSONSchema7): FormlyFieldConfig {
    mappedField.props = mappedField.props ?? {};
    mappedField.validation = { show: true };

    if (!mappedField.props.label && mappedField.key) {
      mappedField.props.label = mappedField.key.toString();
    }

    if (mappedField.type === 'string') {
      if (this.isDateType(mapSource)) {
        mappedField.type = 'datepicker';
        mappedField.parsers = this.wrapDateToStringParser(mappedField.parsers, {
          representation: 'date',
        });
        mappedField.props.readonly = true;
      } else if (this.isDatetimeType(mapSource)) {
        mappedField.type = 'datetime';
        mappedField.parsers = this.wrapDateToStringParser(mappedField.parsers);
      } else if (this.isDurationType(mapSource)) {
        mappedField.type = 'duration';
      }
    }

    const entityType = this.parseEntityRef(mappedField, mapSource);
    if (entityType) {
      return entityType;
    }

    const anyOf = this.parseAnyOfOneOfFormats(mappedField, mapSource);
    if (anyOf) {
      return anyOf;
    }

    return mappedField;
  }

  private wrapDateToStringParser(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    parsers: ((value: any) => any)[] | undefined,
    options?: {
      format?: 'extended' | 'basic';
      representation?: 'complete' | 'date' | 'time';
    }
  ): ((value: unknown) => unknown)[] | undefined {
    if (parsers) {
      return parsers.map((x) => {
        return (v) => {
          if (_.isDate(v)) {
            return formatISO(v, options);
          }
          return x(v);
        };
      });
    }
    return undefined;
  }

  private parseAnyOfOneOfFormats(
    mappedField: FormlyFieldConfig,
    mapSource: JSONSchema7
  ): FormlyFieldConfig | undefined {
    const anyOrOne = _.find(['anyOf' as const, 'oneOf' as const], (anyOneOf) => anyOneOf in mapSource);
    if (anyOrOne) {
      const value = _.get(mapSource, anyOrOne);
      if (_.isArray(value) && _.every(value, (x) => !_.isBoolean(x))) {
        const formats = this.parseFormats(value as JSONSchema7[], mappedField, mapSource);
        if (formats) return formats;
      }
    }
    return undefined;
  }

  private parseFormats(
    value: JSONSchema7[],
    mappedField: FormlyFieldConfig,
    mapSource: JSONSchema7
  ): FormlyFieldConfig | undefined {
    if (
      this.isStringType<JSONSchema7>(mapSource) &&
      value.every((x) => this.isStringType(x) || this.isFormatValue(x))
    ) {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { anyOf, oneOf, ...mapSourceNoOf } = mapSource;
      const { fieldGroup, formatMatchers } = _.reduce(
        value,
        (prev, curr, index) => {
          let format: StringFormat | undefined = undefined;
          if (this.isFormatValue(curr)) {
            format = curr.format;
          } else if (this.isStringType(curr)) {
            format = 'transient';
          }

          if (!format) throw new Error(`Unknown format while building formly config by schema.`, { cause: mapSource });

          const field = this.createFieldConfig({ ...mapSourceNoOf, format });
          const matcher = this.createStringFormatFieldMatcher(format);
          const mergedField = this.mergeDeep(field, mappedField);

          prev.fieldGroup.push({ ...mergedField, key: mappedField.key });
          prev.formatMatchers.push({ ...matcher, fieldGroupIndex: index });
          return prev;
        },
        {
          fieldGroup: [] as FormlyFieldConfig[],
          formatMatchers: [] as StringFormatFieldGroupMatcher[],
        }
      );
      return {
        type: 'string-format',
        props: {
          ...mappedField.props,
          stringFormatOptions: { formatMatchers },
        },
        fieldGroup,
      };
    }
    return undefined;
  }

  private mergeDeep<T>(left: T, right: T): T {
    return _.mergeWith(left, right, (leftVal, rightVal) => {
      if (_.isArray(leftVal) || _.isArray(rightVal)) {
        return _.uniq([...(leftVal ?? []), ...(rightVal ?? [])]);
      }
      if (_.isFunction(leftVal)) {
        return leftVal;
      }
      if (_.isFunction(rightVal)) {
        return rightVal;
      }
      if (_.isObject(leftVal) || _.isObject(rightVal)) {
        return this.mergeDeep(leftVal ?? {}, rightVal ?? {});
      }
      return leftVal ?? rightVal;
    });
  }

  private createStringFormatFieldMatcher(format: StringFormat) {
    if (!StringFormatMatchers.has(format)) {
      throw new Error(`Unknown format ('${format}') while creating 'StringFormatFieldMatcher'.`);
    }

    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return StringFormatMatchers.get(format)!;
  }

  private parseEntityRef(mappedField: FormlyFieldConfig, mapSource: JSONSchema7): FormlyFieldConfig | undefined {
    let entityTypes: EntityType | EntityType[] | undefined;
    if (this._isRef(mapSource)) {
      entityTypes =
        this._refHelper.getEntityRefDefType(mapSource.$ref) ?? this._refHelper.getEntityRefTypesDef(mapSource.$ref);
    } else if (this._isId(mapSource)) {
      entityTypes =
        this._refHelper.getEntityRefDefIdType(mapSource.$id) ??
        this._refHelper.getMultiEntityRefDefIdType(mapSource.$id);
    }

    if (entityTypes) {
      return {
        ...mappedField,
        type: 'entity-lookup',
        props: {
          ...mappedField.props,
          lookupOptions: {
            entityTypes: _.isArray(entityTypes) ? entityTypes : [entityTypes],
          },
        },
      };
    }

    return undefined;
  }

  private _isId(obj: unknown): obj is { $id: string } {
    return _.isObject(obj) && '$id' in obj && _.isString(obj.$id);
  }

  private _isRef(obj: unknown): obj is { $ref: string } {
    return _.isObject(obj) && '$ref' in obj && _.isString(obj.$ref);
  }

  private isFormatValue(obj: unknown): obj is { format: StringFormat } {
    return (
      _.isObject(obj) &&
      'format' in obj &&
      _.isString(obj.format) &&
      StringFormatValues.includes(obj.format as StringFormat)
    );
  }

  private isStringType<T = unknown>(value: T): value is { type: 'string' } & T {
    return _.isObject(value) && 'type' in value && value.type === 'string';
  }

  private isDateType(value: unknown): value is { type: 'string'; format: 'date' } {
    return this.isStringType(value) && 'format' in value && value.format === 'date';
  }

  private isDatetimeType(value: unknown): value is { type: 'string'; format: 'datetime' | 'date-time' } {
    return (
      this.isStringType(value) && 'format' in value && (value.format === 'datetime' || value.format === 'date-time')
    );
  }

  private isDurationType(value: unknown): value is { type: 'string'; format: 'duration'; [key: string]: unknown } {
    return this.isStringType(value) && 'format' in value && value.format === 'duration';
  }
}
