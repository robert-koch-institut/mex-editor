import { Injectable } from '@angular/core';
import { EntityRuleSetSaverService } from './entity-rule-set-saver.service';
import {
  EntityRuleSet,
  NewEntityRuleSet,
  NewEntityRuleSetForEntities,
  isEntityRuleSet,
  isNewEntityRuleSet,
} from '../models/entity-rule-set';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { log } from '../util/log-method.decorator';

@Injectable({
  providedIn: 'root',
})
export class ApiEntityRuleSetSaverService extends EntityRuleSetSaverService {
  constructor(private _http: HttpClient) {
    super();
  }

  override save(ruleSet: EntityRuleSet | NewEntityRuleSet | NewEntityRuleSetForEntities): Observable<EntityRuleSet> {
    if (isNewEntityRuleSet(ruleSet)) {
      return this._create(ruleSet);
    }
    if (isEntityRuleSet(ruleSet)) {
      return this._update(ruleSet);
    }

    return this._createForEntitites(ruleSet.stableTargetId, ruleSet.ruleSet);
  }

  @log('in')
  private _createForEntitites(stableTargetId: string, ruleSet: NewEntityRuleSet) {
    return this._http.post<EntityRuleSet>(`${environment.apiBaseUrl}/v0/rule-set`, { ...ruleSet, stableTargetId });
  }

  @log('in')
  private _create(ruleSet: NewEntityRuleSet): Observable<EntityRuleSet> {
    return this._http.post<EntityRuleSet>(`${environment.apiBaseUrl}/v0/rule-set`, ruleSet);
  }

  @log('in')
  private _update(ruleSet: EntityRuleSet): Observable<EntityRuleSet> {
    return this._http.put<EntityRuleSet>(`${environment.apiBaseUrl}/v0/rule-set`, ruleSet);
  }
}
