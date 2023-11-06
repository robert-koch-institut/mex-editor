import { EntityType } from './entity-type';
import { JSONObject } from './json-object';

export interface Entity extends JSONObject {
  $type: EntityType;

  identifier: string;
  stableTargetId: string;
  hadPrimarySource: string;
}
