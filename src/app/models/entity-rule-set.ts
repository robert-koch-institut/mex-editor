import { isObject, isString } from 'lodash-es';
import { hasValidProperty } from '../util/name-of';

export interface EntityRuleSet {
  stableTargetId: string;
  hadPrimarySource: string;

  [key: string]: ValueRuleSet | string | undefined;
}

export interface NewEntityRuleSet {
  hadPrimarySource: string;

  [key: string]: ValueRuleSet | string | undefined;
}

export interface NewEntityRuleSetForEntities {
  stableTargetId: string;
  ruleSet: NewEntityRuleSet;
}

export function isEntityRuleSet(obj: unknown): obj is EntityRuleSet {
  return isNewEntityRuleSet(obj) && hasValidProperty<EntityRuleSet, string>(obj, 'stableTargetId', isString);
}

export function isNewEntityRuleSet(obj: unknown): obj is NewEntityRuleSet {
  return isObject(obj) && hasValidProperty<EntityRuleSet, string>(obj, 'hadPrimarySource', isString);
}

export interface ValueRuleSet {
  blockPrimarySource?: string[]; // liste der ids die nicht in entity.hadPrimarySource sein dürfen => toggle-hadPrimarySource groupKey false
  blockValue?: unknown[]; // Liste von strings, die nicht in den werten sein dürfen => toggle-wert false
  addValue?: unknown; //
}
