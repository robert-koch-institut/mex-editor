import { Observable } from 'rxjs';
import { JSONSchema7 } from 'json-schema';
import { EntityType } from '../models/entity-type';
import { MergedEntityType } from '../models/merged-entity-type';

export abstract class SchemaLoaderService {
  abstract loadSchema(type: EntityType | MergedEntityType): Observable<JSONSchema7>;
}
