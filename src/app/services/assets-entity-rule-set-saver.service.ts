import { Injectable } from '@angular/core';
import { delay, of, tap } from 'rxjs';
import { EntityRuleSet, NewEntityRuleSet } from '../models/entity-rule-set';
import { EntityRuleSetSaverService } from './entity-rule-set-saver.service';
import RandExp from 'randexp';

@Injectable({
  providedIn: 'root',
})
export class AssetsEntityRuleSetSaverService extends EntityRuleSetSaverService {
  private readonly _idGenerator = new RandExp(/^[a-zA-Z0-9]{14,22}$/);

  override save(ruleSet: EntityRuleSet | NewEntityRuleSet) {
    const saved = { ...ruleSet, stableTargetId: this._idGenerator.gen() };
    return of(saved).pipe(
      delay(2000),
      tap((x) => console.log('SAVED', x))
    );
  }
}
