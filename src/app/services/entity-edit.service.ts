import { Injectable } from '@angular/core';
import { EntityLoaderService } from './entity-loader.service';
import { SchemaLoaderService } from './schema-loader.service';
import { EntityRuleSetLoaderService } from './entity-rule-set-loader.service';
import { Observable, catchError, combineLatest, map, of, switchMap } from 'rxjs';
import { uniq } from 'lodash-es';
import { NewEntityRuleSet } from '../models/entity-rule-set';
import { metadataEditorPrimarySourceId } from '../models/constants';
import { Entity } from '../models/entity';
import { EntityRuleSet } from '../models/entity-rule-set';
import { JSONSchema7 } from 'json-schema';

export interface EntityEdit {
  stableTargetId: string;
  entities: Entity[];
  ruleSet: EntityRuleSet | NewEntityRuleSet;
  schema: JSONSchema7;
}

@Injectable({
  providedIn: 'root',
})
export class EntityEditService {
  constructor(
    private _entityLoader: EntityLoaderService,
    private _schemaLoader: SchemaLoaderService,
    private _ruleSetLoader: EntityRuleSetLoaderService
  ) {}

  loadEntityEdit(stableTargetId: string): Observable<EntityEdit> {
    const entitiesWithSchema$ = this._entityLoader.loadEntities(stableTargetId).pipe(
      switchMap((entities) => {
        const types = uniq(entities.map((x) => x.$type));
        if (types.length !== 1)
          throw new Error(`Unable to determine 'entityType' for 'stableTargetId' = '${stableTargetId}'.`);
        return this._schemaLoader.loadSchema(types[0]).pipe(map((schema) => ({ entities, schema })));
      })
    );

    return combineLatest([
      entitiesWithSchema$,
      this._ruleSetLoader.loadRuleSet(stableTargetId).pipe(
        catchError(() => {
          const emptyRuleSet: NewEntityRuleSet = {
            hadPrimarySource: metadataEditorPrimarySourceId,
          };
          return of(emptyRuleSet);
        })
      ),
    ]).pipe(
      map(([ews, ruleSet]) => {
        return { stableTargetId, entities: ews.entities, ruleSet, schema: ews.schema };
      })
    );
  }
}
