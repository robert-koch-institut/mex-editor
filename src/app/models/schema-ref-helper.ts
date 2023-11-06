import * as _ from 'lodash-es';
import { EntityType, EntityTypeValues } from './entity-type';

export class SchemaRefHelper {
  private readonly entityIdentifierRefRegEx = new RegExp(
    `^#/components/schemas/(${EntityTypeValues.join('|')})ID$`,
    'm'
  );

  isEntityRef(ref: string): boolean {
    return this.entityIdentifierRefRegEx.test(ref);
  }
  getEntityRefType(ref: string): EntityType | undefined {
    if (this.isEntityRef(ref)) {
      const extract = ref.replace(this.entityIdentifierRefRegEx, '$1') as EntityType;
      if (EntityTypeValues.includes(extract)) {
        return extract;
      }
    }
    return undefined;
  }
  buildEntityRefDef(entityType: EntityType) {
    return `#/$defs/entity-identifier/${entityType}`;
  }
  private entityRefDefRegEx = new RegExp(`^#/\\$defs/entity-identifier/(${EntityTypeValues.join('|')})$`, 'm');
  isEntityRefDefType(def: string) {
    return this.entityRefDefRegEx.test(def);
  }
  getEntityRefDefType(def: string): EntityType | undefined {
    if (this.isEntityRefDefType(def)) {
      const extract = def.replace(this.entityRefDefRegEx, '$1') as EntityType;
      if (EntityTypeValues.includes(extract)) {
        return extract;
      }
    }
    return undefined;
  }

  buildEntityRefDefId(entityType: EntityType) {
    return `https://mex.rki.de/schema/entity-identifier/${entityType}`;
  }
  private entityRefDefIdRegEx = new RegExp(
    `^https://mex.rki.de/schema/entity-identifier/(${EntityTypeValues.join('|')})$`,
    'm'
  );
  isEntityRefDefId(id: string) {
    return this.entityRefDefIdRegEx.test(id);
  }
  getEntityRefDefIdType(id: string): EntityType | undefined {
    if (this.isEntityRefDefId(id)) {
      const extract = id.replace(this.entityRefDefIdRegEx, '$1') as EntityType;
      if (EntityTypeValues.includes(extract)) {
        return extract;
      }
    }
    return undefined;
  }

  areEntityRefs(refs: string[]): boolean {
    return _.every(refs, (x) => this.isEntityRef(x));
  }
  getEntityRefTypes(refs: string[]): EntityType[] | undefined {
    if (this.areEntityRefs(refs)) {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      return refs.map((x) => this.getEntityRefType(x)!);
    }
    return undefined;
  }
  buildEntityRefTypesDef(entityRefTypes: EntityType[]): string {
    this._ensureArgumentHasItems('entityRefTypes', entityRefTypes);
    return `#/$defs/multi-entity-identifier/${entityRefTypes.join('|')}`;
  }
  private entityRefDefsRegEx = new RegExp(
    `^#/\\$defs/multi-entity-identifier/((${EntityTypeValues.join('|')}|\\|)+)$`,
    'm'
  );
  isEntityRefTypesDef(def: string): boolean {
    return this.entityRefDefsRegEx.test(def);
  }
  getEntityRefTypesDef(def: string): EntityType[] | undefined {
    if (this.isEntityRefTypesDef(def)) {
      const extract = def.replace(this.entityRefDefsRegEx, '$1');
      const extracts = extract.split('|') as EntityType[];
      if (extracts.every((x) => EntityTypeValues.includes(x))) {
        return extracts;
      }
    }
    return undefined;
  }

  private multiEntityRefDefIdRegEx = new RegExp(
    `^https://mex.rki.de/schema/multi-entity-identifier/((${EntityTypeValues.join('|')}|\\|)+)$`,
    'm'
  );
  isMultiEntityRefDefId(id: string) {
    return this.multiEntityRefDefIdRegEx.test(id);
  }
  getMultiEntityRefDefIdType(id: string): EntityType[] | undefined {
    if (this.isMultiEntityRefDefId(id)) {
      const extract = id.replace(this.multiEntityRefDefIdRegEx, '$1') as EntityType;
      const extracts = extract.split('|') as EntityType[];
      if (extracts.every((x) => EntityTypeValues.includes(x))) {
        return extracts;
      }
    }
    return undefined;
  }
  buildMultiEntityRefDefId(entityTypes: EntityType[]) {
    return `https://mex.rki.de/schema/multi-entity-identifier/${entityTypes.join('|')}`;
  }

  private _ensureArgumentHasItems(argName: string, argValue: unknown[]) {
    if (argValue.length === 0) {
      throw new Error(`Argument '${argName}' has to contain at least 1 item.`);
    }
  }
}
