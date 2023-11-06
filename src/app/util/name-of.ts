import { get } from 'lodash-es';

export const nameOf = <T>(name: Extract<keyof T, string>): keyof T & string => name;

export const hasValidProperty = <T, K>(
  obj: object,
  propName: keyof T,
  valueGuard: (value: unknown) => value is K
): obj is Record<keyof T, K> => {
  const value = get(obj, propName);
  return valueGuard(value);
};
