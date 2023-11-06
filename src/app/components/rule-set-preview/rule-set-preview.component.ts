import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Observable, map, of } from 'rxjs';
import { nameOf } from 'src/app/util/name-of';
import { EntityRuleSet, NewEntityRuleSetForEntities } from 'src/app/models/entity-rule-set';
import { log } from 'src/app/util/log-method.decorator';
import { EntityRuleSetPreviewService } from 'src/app/services/entity-rule-set-preview.service';
import { toPairs } from 'lodash-es';

@Component({
  selector: 'app-rule-set-preview',
  templateUrl: './rule-set-preview.component.html',
  styleUrls: ['./rule-set-preview.component.scss'],
})
export class RuleSetPreviewComponent implements OnChanges {
  @Input() ruleSet?: EntityRuleSet | NewEntityRuleSetForEntities;
  preview$: Observable<[string, string][] | undefined> = of(undefined);

  constructor(private _ruleSetPreview: EntityRuleSetPreviewService) {}

  @log('in')
  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<RuleSetPreviewComponent>('ruleSet') in changes) {
      this._updatePreview();
    }
  }

  private _updatePreview() {
    this.preview$ = this.ruleSet
      ? this._ruleSetPreview.preview(this.ruleSet).pipe(map((x) => toPairs(x).map(([k, v]) => [k, JSON.stringify(v)])))
      : of(undefined);
  }
}
