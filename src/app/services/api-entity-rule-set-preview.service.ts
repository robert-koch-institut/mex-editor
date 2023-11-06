import { Injectable } from '@angular/core';
import { EntityRuleSetPreviewService } from './entity-rule-set-preview.service';
import { Observable } from 'rxjs';
import { EntityRuleSet, NewEntityRuleSetForEntities, isEntityRuleSet } from '../models/entity-rule-set';
import { MergedEntity } from '../models/merged-entity';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { log } from '../util/log-method.decorator';

@Injectable({
  providedIn: 'root',
})
export class ApiEntityRuleSetPreviewService extends EntityRuleSetPreviewService {
  constructor(private _http: HttpClient) {
    super();
  }

  @log('in')
  override preview(ruleSet: EntityRuleSet | NewEntityRuleSetForEntities): Observable<MergedEntity> {
    const body = isEntityRuleSet(ruleSet) ? ruleSet : { ...ruleSet.ruleSet, stableTargetId: ruleSet.stableTargetId };
    const { hadPrimarySource, ...bodyNoHasPrimarySource } = body;
    return this._http.post<MergedEntity>(`${environment.apiBaseUrl}/v0/preview`, bodyNoHasPrimarySource);
  }
}
