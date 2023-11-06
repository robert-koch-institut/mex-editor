import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { cloneDeep } from 'lodash-es';
import { combineLatest, map, Observable, of } from 'rxjs';
import {
  DefaultEntitySearch,
  DefaultPageSize,
  MergedEntitySearch,
  MergedEntitySearchComponent,
} from 'src/app/components/merged-entity-search/merged-entity-search.component';
import { MergedEntityType, MergedEntityTypeValues, isMergedEntityType } from 'src/app/models/merged-entity-type';
import { log } from 'src/app/util/log-method.decorator';

@Component({
  selector: 'app-entity-search-page',
  templateUrl: './entity-search-page.component.html',
  styleUrls: ['./entity-search-page.component.scss'],
})
export class EntitySearchPageComponent implements OnInit, AfterViewInit {
  @ViewChild(MergedEntitySearchComponent)
  entitySearchComponent?: MergedEntitySearchComponent;

  entitySearch$?: Observable<MergedEntitySearch> = of(cloneDeep(DefaultEntitySearch));

  constructor(private _route: ActivatedRoute, private _router: Router) {}

  ngOnInit(): void {
    this.entitySearch$ = this.createSearchByUrl();
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (this.entitySearchComponent) {
        this.entitySearchComponent.search();
      }
    });
  }

  private createSearchByUrl() {
    const query$ = this._route.paramMap.pipe(
      map((x) => {
        return x.has('query') ? x.get('query') ?? '' : '';
      })
    );

    const filterPagination$ = this._route.queryParamMap.pipe(
      map((x) => {
        const entityTypes = x.has('entitytype')
          ? (x.getAll('entitytype').filter((x) => isMergedEntityType(x)) as MergedEntityType[])
          : [...MergedEntityTypeValues];

        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const index = x.has('page') ? parseInt(x.get('page')!) : 0;
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const size = x.has('size') ? parseInt(x.get('size')!) : DefaultPageSize;

        return { filter: { entityTypes }, page: { index, size } };
      })
    );

    return combineLatest([query$, filterPagination$]).pipe(
      map(([query, fp]) => {
        const { filter, page } = fp;
        return { query, filter, page };
      })
    );
  }

  onEntitySearchChanged(entitySearch: MergedEntitySearch) {
    this.updateUrlParams(entitySearch);
  }

  @log('in')
  updateUrlParams(entitySearch: MergedEntitySearch) {
    const { query, filter, page } = entitySearch;

    const url = query !== undefined ? ['/search', query] : this._route.snapshot.url.map((x) => x.path);
    const queryParams: Params = { ...this._route.snapshot.queryParams };
    if (filter) {
      if (filter.entityTypes && filter.entityTypes.length !== MergedEntityTypeValues.length) {
        queryParams['entitytype'] = filter.entityTypes;
      }
    }
    if (page !== undefined) {
      if (page.index !== 0) {
        queryParams['page'] = page.index;
      }
      if (page.size !== DefaultPageSize) {
        queryParams['size'] = page.size;
      }
    }
    console.log('UPDATING URL PARAMS', url, queryParams);
    this._router.navigate(url, { queryParams });
  }
}
