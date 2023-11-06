import { Observable } from 'rxjs';
import { MergedEntityType } from '../models/merged-entity-type';
import { MergedEntity } from '../models/merged-entity';
import { MergedEntitySearch } from '../components/merged-entity-search/merged-entity-search.component';

export interface MergedEntitySearchFilter {
  entityTypes?: readonly MergedEntityType[];
}
export interface MergedEntitySearchResult {
  search: MergedEntitySearch;

  entities: MergedEntity[];
  totalEntities: number;
}

export abstract class EntitySearchService {
  abstract search(entitySearch: MergedEntitySearch): Observable<MergedEntitySearchResult>;
}
