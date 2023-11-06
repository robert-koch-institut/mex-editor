import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { metadataEditorPrimarySourceId } from '../models/constants';
import { EntityRuleSet } from '../models/entity-rule-set';
import { EntityRuleSetLoaderService } from './entity-rule-set-loader.service';

@Injectable({
  providedIn: 'root',
})
export class AssetsEntityRuleSetLoaderService extends EntityRuleSetLoaderService {
  private ruleSets: Record<string, EntityRuleSet> = {
    '00000000-0000-4000-8000-00002620b583': {
      hadPrimarySource: metadataEditorPrimarySourceId,
      stableTargetId: '00000000-0000-4000-8000-00002620b583',
      familyName: {
        blockValue: ['Brot'],
        addValue: ['NACHNAME mexEditorValue'],
        blockPrimarySource: [],
      },
      email: {
        blockPrimarySource: ['00000000-0000-4000-8000-000095ff358d#merged'],
      },
    },
  };

  override loadRuleSet(stableTargetId: string): Observable<EntityRuleSet> {
    return of(
      stableTargetId in this.ruleSets
        ? this.ruleSets[stableTargetId]
        : { stableTargetId, hadPrimarySource: metadataEditorPrimarySourceId }
    );
  }
}
