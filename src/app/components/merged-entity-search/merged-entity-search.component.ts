import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PageEvent } from '@angular/material/paginator';
import { cloneDeep } from 'lodash-es';
import { Observable, of } from 'rxjs';
import { MergedEntity } from 'src/app/models/merged-entity';
import { MergedEntityType, MergedEntityTypeValues } from 'src/app/models/merged-entity-type';
import {
  EntitySearchService,
  MergedEntitySearchFilter,
  MergedEntitySearchResult,
} from 'src/app/services/entity-search.service';
import { log } from 'src/app/util/log-method.decorator';

export interface Pagination {
  index: number;
  size: number;
}

export const DefaultPageSize = 10;
export const AvailablePageSizes = [5, DefaultPageSize, 15, 20, 25];
export const DefaultEntitySearch = {
  query: '',
  filter: { entityTypes: [...MergedEntityTypeValues] },
  page: { index: 0, size: DefaultPageSize },
};

export interface MergedEntitySearch {
  query: string;
  filter: MergedEntitySearchFilter;
  page: Pagination;
}

@Component({
  selector: 'app-merged-entity-search',
  templateUrl: './merged-entity-search.component.html',
  styleUrls: ['./merged-entity-search.component.scss'],
})
export class MergedEntitySearchComponent {
  @Input() enableFilter = true;
  @Input() enableNavigation = true;
  @Input() enableSelection = true;

  @Input() availableEntityTypes = [...MergedEntityTypeValues];

  @Input() entitySearch: MergedEntitySearch = cloneDeep(DefaultEntitySearch);
  @Output() entitySearchChanged = new EventEmitter<MergedEntitySearch>();

  selectedEntity?: MergedEntity;
  @Output() selectedEntityChanged = new EventEmitter<MergedEntity | undefined>();

  searchResult$: Observable<MergedEntitySearchResult> = of({
    search: {
      query: '',
      filter: { entityTypes: this.availableEntityTypes },
      page: { size: DefaultPageSize, index: 0 },
    },
    totalEntities: 0,
    entities: [],
  });
  pageSizeOptions = AvailablePageSizes;

  constructor(private _entitySearchService: EntitySearchService) {}

  array(size: number) {
    return new Array(size);
  }

  @log('in')
  search() {
    this.searchResult$ = this._entitySearchService.search(this.entitySearch);
  }

  selectEntity(entity: MergedEntity | undefined) {
    if (this.enableSelection) {
      this.selectedEntity = entity;
      this.selectedEntityChanged.emit(entity);
    }
  }

  onPageChanged(page: PageEvent) {
    const update = cloneDeep(this.entitySearch);
    update.page = { index: page.pageIndex, size: page.pageSize };
    this.entitySearch = update;
    this.entitySearchChanged.emit(update);
  }

  onSearchQueryChanged(query: string) {
    const update = cloneDeep(this.entitySearch);
    update.query = query;
    this.entitySearch = update;
    this.entitySearchChanged.emit(update);
  }

  @log('in')
  onEntityTypeFilterChanged(entityTypes: MergedEntityType[]) {
    if (this.enableFilter) {
      const update = cloneDeep(this.entitySearch);
      update.filter.entityTypes = entityTypes;
      this.entitySearch = update;
      this.entitySearchChanged.emit(update);
    }
  }
}
