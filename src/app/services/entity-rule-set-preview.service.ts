import { Observable } from 'rxjs';
import { EntityRuleSet, NewEntityRuleSetForEntities } from '../models/entity-rule-set';
import { MergedEntity } from '../models/merged-entity';

export abstract class EntityRuleSetPreviewService {
  abstract preview(ruleSet: EntityRuleSet | NewEntityRuleSetForEntities): Observable<MergedEntity>;
}
