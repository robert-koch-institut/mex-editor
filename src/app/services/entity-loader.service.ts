import { Observable } from 'rxjs';
import { Entity } from '../models/entity';
import { MergedEntity } from '../models/merged-entity';

export abstract class EntityLoaderService {
  abstract loadEntities(stableTargetId: string): Observable<Entity[]>;
  abstract loadMergedEntity(stableTargetId: string): Observable<MergedEntity>;
}
