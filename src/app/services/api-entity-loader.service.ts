import { Injectable } from '@angular/core';
import { EntityLoaderService } from './entity-loader.service';
import { Observable, map } from 'rxjs';
import { Entity } from '../models/entity';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { MergedEntity } from '../models/merged-entity';

interface ExtractedItemResponse {
  total: number;
  items: Entity[];
}

@Injectable({
  providedIn: 'root',
})
export class ApiEntityLoaderService extends EntityLoaderService {
  constructor(private _http: HttpClient) {
    super();
  }

  override loadEntities(stableTargetId: string): Observable<Entity[]> {
    const params = new HttpParams().set('stableTargetId', stableTargetId);

    return this._http
      .get<ExtractedItemResponse>(`${environment.apiBaseUrl}/v0/extracted-item`, { params })
      .pipe(map((x) => x.items));
  }

  override loadMergedEntity(stableTargetId: string): Observable<MergedEntity> {
    return this._http.get<MergedEntity>(`${environment.apiBaseUrl}/v0/merged-item/${stableTargetId}`);
  }
}
