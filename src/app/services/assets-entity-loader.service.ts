import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import * as _ from 'lodash-es';
import { combineLatest, delay, map, Observable, shareReplay } from 'rxjs';
import { Entity } from '../models/entity';
import { EntityType, EntityTypeValues } from '../models/entity-type';
import { JSONObject } from '../models/json-object';
import { EntityLoaderService } from './entity-loader.service';
import { MergedEntity } from '../models/merged-entity';
import { MergedEntityType } from '../models/merged-entity-type';

@Injectable({
  providedIn: 'root',
})
export class AssetsEntityLoaderService extends EntityLoaderService {
  private _allEntities$ = combineLatest(
    EntityTypeValues.map((type) =>
      this.http
        .get<JSONObject[]>(`/assets/data/${_.kebabCase(type)}.json`)
        .pipe(map((x) => [type, x.map((e) => this.createEntity(e, type))] as [EntityType, Entity[]]))
    )
  )
    .pipe(
      map((x) => {
        return x.reduce((prev, curr) => {
          const [type, entites] = curr;
          prev.set(type, entites);
          return prev;
        }, new Map<EntityType, Entity[]>());
      })
    )
    .pipe(shareReplay(1));

  constructor(private http: HttpClient) {
    super();
  }

  loadAllEntities(type: EntityType): Observable<Entity[]> {
    return this._allEntities$.pipe(
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      map((x) => (x.has(type) ? x.get(type)! : []))
    );
  }

  override loadEntities(stableTargetId: string) {
    return this._allEntities$.pipe(
      map((x) => {
        const entities = [...x.values()];
        return _.filter(_.flatMap(entities), (e) => 'stableTargetId' in e && e['stableTargetId'] === stableTargetId);
      })
    );
  }

  override loadMergedEntity(stableTargetId: string): Observable<MergedEntity> {
    return this._allEntities$.pipe(
      map((x) => {
        const entities = [...x.values()];
        const found = _.find(
          _.flatMap(entities),
          (e) => 'stableTargetId' in e && e['stableTargetId'] === stableTargetId
        );

        if (!found) {
          throw new Error('Not Found');
        }

        return { ...found, $type: `Merged${found.$type}` as MergedEntityType };
      }),
      delay(3000)
    );
  }

  private createEntity(json: JSONObject, $type: EntityType) {
    if (!('identifier' in json) || !_.isString(json['identifier'])) {
      throw new Error(`Can't create entity (type=${$type}) from given json. Field 'identifier' is missing.`, {
        cause: json,
      });
    }

    if (!('stableTargetId' in json) || !_.isString(json['stableTargetId'])) {
      throw new Error(`Can't create entity (type=${$type}) from given json. Field 'stableTargetId' is missing.`, {
        cause: json,
      });
    }

    if (!('hadPrimarySource' in json) || !_.isString(json['hadPrimarySource'])) {
      throw new Error(`Can't create entity (type=${$type}) from given json. Field 'hadPrimarySource' is missing.`, {
        cause: json,
      });
    }

    const entity: Entity = {
      ...json,
      $type,
      identifier: json['identifier'],
      stableTargetId: json['stableTargetId'],
      hadPrimarySource: json['hadPrimarySource'],
    };
    return entity;
  }
}
