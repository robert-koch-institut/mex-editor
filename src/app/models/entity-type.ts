import { JSONSchema7 } from 'json-schema';
import { isString } from 'lodash-es';

export const EntityTypeValues = [
  'Person',
  'Resource',
  'Organization',
  'AccessPlatform',
  'Activity',
  'ContactPoint',
  'Distribution',
  'OrganizationalUnit',
  'PrimarySource',
  'VariableGroup',
  'Variable',
] as const;
export type EntityTypeTuple = typeof EntityTypeValues;
export type EntityType = EntityTypeTuple[number];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function isEntityType(value: any): value is EntityType {
  return isString(value) && EntityTypeValues.includes(value as EntityType);
}

export function mapLabel(value: EntityType, propSchema?: JSONSchema7) {
  if (propSchema && propSchema.title) {
    return propSchema.title;
  }

  switch (value) {
    case 'AccessPlatform':
      return 'Zugangsplattform';
    case 'Activity':
      return 'Aktivität';
    case 'ContactPoint':
      return 'Kontaktpunkt';
    case 'Distribution':
      return 'Verteilung';
    case 'Organization':
      return 'Organisation';
    case 'OrganizationalUnit':
      return 'Organisationseinheit';
    case 'Person':
      return 'Person';
    case 'PrimarySource':
      return 'Primäre Quelle';
    case 'Resource':
      return 'Resource';
    case 'Variable':
      return 'Variable';
    case 'VariableGroup':
      return 'Variablengruppe';
    default:
      return `Unbekannte Entität (${value})`;
  }
}
