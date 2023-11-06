import { Injectable } from '@angular/core';
import { EntitySearchService, MergedEntitySearchResult } from './entity-search.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Entity } from '../models/entity';
import { MergedEntity } from '../models/merged-entity';
import { MergedEntitySearch } from '../components/merged-entity-search/merged-entity-search.component';

interface MergedItemResponse {
  total: number;
  items: MergedEntity[];
}

interface ExtractedItemResponse {
  total: number;
  items: Entity[];
}

@Injectable({
  providedIn: 'root',
})
export class ApiEntitySearchService extends EntitySearchService {
  constructor(private _http: HttpClient) {
    super();
  }

  override search(entitySearch: MergedEntitySearch): Observable<MergedEntitySearchResult> {
    const { query, filter, page } = entitySearch;
    const params = new HttpParams({
      fromObject: {
        q: query,
        entityType: filter.entityTypes ?? [],
        skip: page.index * page.size,
        limit: page.size,
      },
    });
    return this._http.get<MergedItemResponse>(`${environment.apiBaseUrl}/v0/merged-item`, { params }).pipe(
      map((x) => {
        return {
          search: entitySearch,
          entities: x.items,
          totalEntities: x.total,
        };
      })
    );
  }
}
