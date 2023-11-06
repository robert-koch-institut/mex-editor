import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import * as _ from 'lodash-es';
import { combineLatest, map, Observable, of, shareReplay } from 'rxjs';
import { AssetsEntityRuleSetLoaderService } from 'src/app/services/assets-entity-rule-set-loader.service';
import { SchemaLoaderService } from 'src/app/services/schema-loader.service';
import { EntitySearchService } from 'src/app/services/entity-search.service';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';
import { MergedEntityType, MergedEntityTypeValues } from 'src/app/models/merged-entity-type';

@Component({
  selector: 'app-debug-edit-page',
  templateUrl: './debug-edit-page.component.html',
  styleUrls: ['./debug-edit-page.component.scss'],
})
export class DebugEditPageComponent {
  entityEdits$ = combineLatest(
    MergedEntityTypeValues.map((x) => {
      return combineLatest([
        this._entitySearch.search({ query: '', filter: { entityTypes: [x] }, page: { index: 0, size: 1 } }),
        this._schemaLoader.loadSchema(x),
      ]).pipe(
        map(([e, schema]) => {
          const entity = _.first(e.entities);

          return {
            type: x,
            schema,
            ruleAndEntities$: combineLatest([
              entity ? this._ruleSetLoader.loadRuleSet(entity.stableTargetId) : of(undefined),
              entity ? this._entityLoader.loadEntities(entity.stableTargetId) : of(undefined),
            ]).pipe(
              map(([rule, entities]) => {
                return { rule, entities };
              })
            ),
          };
        })
      );
    })
  )
    .pipe(map((x) => _.flatMap(x)))
    .pipe(shareReplay(1));

  activeTabIndex$: Observable<number | null> = combineLatest([
    this.entityEdits$,
    this._route.queryParamMap.pipe(map((x) => (x.has('tab') ? x.get('tab') : null))),
  ]).pipe(
    map(([edits, tab]) => {
      return tab === null ? 0 : _.findIndex(edits, (x) => x.type === tab);
    })
  );

  updateTabQueryParam(type: MergedEntityType) {
    this._router.navigate([], {
      relativeTo: this._route,
      queryParams: { tab: type },
    });
  }

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    private _entitySearch: EntitySearchService,
    private _entityLoader: EntityLoaderService,
    private _schemaLoader: SchemaLoaderService,
    private _ruleSetLoader: AssetsEntityRuleSetLoaderService // private _dialogService: DialogService
  ) {}
}
