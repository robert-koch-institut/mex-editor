import { Observable } from 'rxjs';
import { EntityRuleSet, NewEntityRuleSet, NewEntityRuleSetForEntities } from '../models/entity-rule-set';

export abstract class EntityRuleSetSaverService {
  abstract save(ruleSet: EntityRuleSet | NewEntityRuleSet | NewEntityRuleSetForEntities): Observable<EntityRuleSet>;
}
