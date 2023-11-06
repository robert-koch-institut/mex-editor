import { JSONObject, JSONValue } from './json-object';
import { MergedEntityType } from './merged-entity-type';

export interface MergedEntity extends JSONObject {
  $type: MergedEntityType;

  identifier: string;
  stableTargetId: string;

  [key: string]: Array<JSONValue> | string;
}
