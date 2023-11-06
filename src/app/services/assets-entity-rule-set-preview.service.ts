import { Injectable } from '@angular/core';
import { EntityRuleSetPreviewService } from './entity-rule-set-preview.service';
import { Observable, of } from 'rxjs';
import { EntityRuleSet, NewEntityRuleSetForEntities, isEntityRuleSet } from '../models/entity-rule-set';
import { MergedEntity } from '../models/merged-entity';

@Injectable({
  providedIn: 'root',
})
export class AssetsEntityRuleSetPreviewService extends EntityRuleSetPreviewService {
  constructor() {
    super();
  }

  override preview(ruleSet: EntityRuleSet | NewEntityRuleSetForEntities): Observable<MergedEntity> {
    if (isEntityRuleSet(ruleSet)) {
      return of({ identifier: '', $type: 'MergedPerson', ...ruleSet, stableTargetId: ruleSet.stableTargetId ?? '' });
    }
    return of({ $type: 'MergedPerson', stableTargetId: ruleSet.stableTargetId, identifier: '', ...ruleSet.ruleSet });
  }
}
