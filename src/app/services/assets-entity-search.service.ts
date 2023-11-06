import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AssetsEntityLoaderService } from './assets-entity-loader.service';
import { EntitySearchService, MergedEntitySearchResult } from './entity-search.service';
import { MergedEntitySearch } from '../components/merged-entity-search/merged-entity-search.component';

@Injectable({
  providedIn: 'root',
})
export class AssetsEntitySearchService extends EntitySearchService {
  constructor(private entityLoader: AssetsEntityLoaderService) {
    super();
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  override search(entitySearch: MergedEntitySearch): Observable<MergedEntitySearchResult> {
    throw new Error('Not implemented!');
  }
}
