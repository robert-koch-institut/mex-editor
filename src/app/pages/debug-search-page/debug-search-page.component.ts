import { Component } from '@angular/core';
import * as _ from 'lodash-es';
import { combineLatest, map, Observable } from 'rxjs';
import { displayEntityFields } from 'src/app/models/constants';
import { MergedEntity } from 'src/app/models/merged-entity';
import { MergedEntityTypeValues } from 'src/app/models/merged-entity-type';
import { EntitySearchService } from 'src/app/services/entity-search.service';

@Component({
  selector: 'app-debug-search-page',
  templateUrl: './debug-search-page.component.html',
  styleUrls: ['./debug-search-page.component.scss'],
})
export class DebugSearchPageComponent {
  entities$: Observable<MergedEntity[]>;

  constructor(private _entitySearch: EntitySearchService) {
    this.entities$ = combineLatest(
      MergedEntityTypeValues.map((x) => {
        return this._entitySearch.search({ query: '', filter: { entityTypes: [x] }, page: { index: 0, size: 1 } }).pipe(
          map((e) =>
            _.find(e.entities, (f) => {
              const displayDef = displayEntityFields[f.$type];
              return 'additionalFields' in displayDef && displayDef.additionalFields
                ? displayDef.additionalFields?.every((a) => !!f[a])
                : true;
            })
          )
        );
      })
    ).pipe(map((x) => _.flatMap(x).filter((x) => x !== undefined) as MergedEntity[]));
  }
}
