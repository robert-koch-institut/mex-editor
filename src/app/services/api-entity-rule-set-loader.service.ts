import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { EntityRuleSetLoaderService } from './entity-rule-set-loader.service';
import { Observable } from 'rxjs';
import { EntityRuleSet } from '../models/entity-rule-set';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiEntityRuleSetLoaderService extends EntityRuleSetLoaderService {
  constructor(private _http: HttpClient) {
    super();
  }

  override loadRuleSet(stableTargetId: string): Observable<EntityRuleSet> {
    return this._http.get<EntityRuleSet>(`${environment.apiBaseUrl}/v0/rule-set/${stableTargetId}`);
  }
}
