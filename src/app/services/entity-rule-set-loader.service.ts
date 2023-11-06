import { Observable } from 'rxjs';
import { EntityRuleSet } from '../models/entity-rule-set';

export abstract class EntityRuleSetLoaderService {
  abstract loadRuleSet(stableTargetId: string): Observable<EntityRuleSet>;
}
