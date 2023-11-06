import { JSONSchema7 } from 'json-schema';
import { EntityType, EntityTypeValues } from './entity-type';
import * as _ from 'lodash-es';
import { SchemaRefHelper } from './schema-ref-helper';

export class JsonSchemaNormalizer {
  private _refHelper = new SchemaRefHelper();

  normalize(schema: JSONSchema7, schemaSource: unknown): JSONSchema7 {
    const multiEntityRefs: EntityType[][] = [];

    const clone = _.cloneDeepWith(schema, (value) => {
      if (this._isRefObj(value)) {
        if (this._refHelper.isEntityRef(value.$ref)) {
          return this._normalizeRef(value);
        }
        const resolvedRef = this._resolveRef(value, schemaSource);
        return this.normalize(resolvedRef, schemaSource);
      }

      if (this._isAnyOfRef(value)) {
        const { anyOf, ...other } = value;
        return this._normalizeRefs({ other, refs: anyOf }, multiEntityRefs);
      }

      if (this._isOneOfRef(value)) {
        const { oneOf, ...other } = value;
        return this._normalizeRefs({ other, refs: oneOf }, multiEntityRefs);
      }

      return undefined;
    }) as JSONSchema7;

    clone.$defs = this._buildDefs(multiEntityRefs);
    return clone;
  }

  private _buildDefs(multiEntityRefs: EntityType[][]) {
    const multiEntityRefDefs = multiEntityRefs.map((x) => {
      const def = {
        title: `${x.join(' oder ')} ${'Identifier'}`,
        pattern: '^[a-zA-Z0-9]{14,22}$',
        type: 'string',
        $id: this._refHelper.buildMultiEntityRefDefId(x),
      };
      return [`multi-entity-identifier/${x.join('|')}`, def] as [string, JSONSchema7];
    });

    const entityIdentifierDefs = _.map(EntityTypeValues, (x) => {
      const def = {
        pattern: '^[a-zA-Z0-9]{14,22}$',
        type: 'string',
        title: `${x} Identifier`,
        $id: this._refHelper.buildEntityRefDefId(x),
      };
      return [`entity-identifier/${x}`, def] as [string, JSONSchema7];
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return [...entityIdentifierDefs, ...multiEntityRefDefs].reduce((defs, refDefs) => {
      const [path, x] = refDefs;
      const parts = path.split('/');
      _.reduce(
        parts,
        (prev, curr, index, array) => {
          if (index === array.length - 1) {
            prev[curr] = x;
          } else if (!(curr in prev)) {
            prev[curr] = {};
          }
          return prev[curr] as { [key: string]: JSONSchema7 };
        },
        defs
      );
      return defs;
    }, {} as { [key: string]: JSONSchema7 });
  }

  private _normalizeRefs(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: { other: any; refs: { $ref: string }[] },
    multiEntityRefs: EntityType[][]
  ): { $ref: string } | undefined {
    const entityRefTypes = this._refHelper.getEntityRefTypes(value.refs.map((x) => x.$ref));
    if (entityRefTypes) {
      multiEntityRefs.push(entityRefTypes);
      return {
        $ref: this._refHelper.buildEntityRefTypesDef(entityRefTypes),
        ...value.other,
      };
    }

    return undefined;
  }

  private _normalizeRef(value: { $ref: string }): JSONSchema7 | undefined {
    const entityRef = this._refHelper.getEntityRefType(value.$ref);
    if (entityRef) {
      return {
        ...value,
        $ref: this._refHelper.buildEntityRefDef(entityRef),
      };
    }
    return undefined;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private _resolveRef(obj: { $ref: string }, source: any) {
    const { $ref, ...others } = obj;
    const [uri, objPointer, propName] = $ref.split('#/');
    if (uri) {
      throw new Error('External pointers not supported.');
    }

    if (propName && propName === 'identifier') {
      return undefined;
    }

    let resolvedObj = objPointer.split('/').reduce((objLookup, path) => {
      if (!(path in objLookup)) {
        throw new Error(`Path '${path}' doesn't exist in object lookup.`);
      }
      return objLookup[path];
    }, source);

    if (propName) {
      if (!('properties' in resolvedObj)) {
        throw new Error(
          `Resolved object isn't a json schema, but there is a property '${propName}' in given path '${$ref}' present.`
        );
      }
      if (!(propName in resolvedObj.properties)) {
        throw new Error(`There is no property '${propName}' in properties of resolved object ('${objPointer}').`);
      }
      resolvedObj = resolvedObj.properties[propName];
    }

    return { ...others, ...resolvedObj };
  }

  private _isRefObj(value: unknown): value is { $ref: string } {
    return _.isObject(value) && '$ref' in value && _.isString(value.$ref);
  }

  private _isOneOfRef(obj: unknown): obj is { oneOf: { $ref: string }[] } {
    return _.isObject(obj) && 'oneOf' in obj && _.isArray(obj.oneOf) && _.every(obj.oneOf, (x) => this._isRefObj(x));
  }

  private _isAnyOfRef(obj: unknown): obj is { anyOf: { $ref: string }[] } {
    return _.isObject(obj) && 'anyOf' in obj && _.isArray(obj.anyOf) && _.every(obj.anyOf, (x) => this._isRefObj(x));
  }
}
