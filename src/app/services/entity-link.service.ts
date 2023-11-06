import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap, map, delay, noop, of } from 'rxjs';
import { MergedEntity } from '../models/merged-entity';
import { isString } from 'lodash-es';

@Injectable({
  providedIn: 'root',
})
export class EntityLinkService {
  constructor(private _http: HttpClient) {}

  linkEntities(leftEntity: MergedEntity | string, rightEntity: MergedEntity | string): Observable<void> {
    const left = isString(leftEntity) ? leftEntity : leftEntity.stableTargetId;
    const right = isString(rightEntity) ? rightEntity : rightEntity.stableTargetId;
    return of([left, right]).pipe(
      map(() => noop()),
      tap(() => console.log(`LINKING Entites`, left, right)),
      delay(2000)
    );
  }
}
