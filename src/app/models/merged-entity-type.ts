import { JSONSchema7 } from 'json-schema';
import { isString } from 'lodash-es';

export const MergedEntityTypeValues = [
  'MergedPerson',
  'MergedResource',
  'MergedOrganization',
  'MergedAccessPlatform',
  'MergedActivity',
  'MergedContactPoint',
  'MergedDistribution',
  'MergedOrganizationalUnit',
  'MergedPrimarySource',
  'MergedVariableGroup',
  'MergedVariable',
] as const;
export type MergedEntityTypeTuple = typeof MergedEntityTypeValues;
export type MergedEntityType = MergedEntityTypeTuple[number];

export function isMergedEntityType(value: unknown): value is MergedEntityType {
  return isString(value) && MergedEntityTypeValues.includes(value as MergedEntityType);
}

export function mapLabel(value: MergedEntityType, propSchema?: JSONSchema7) {
  if (propSchema && propSchema.title) {
    return propSchema.title;
  }

  switch (value) {
    case 'MergedAccessPlatform':
      return 'Zugangsplattform (Zusammengeführt)';
    case 'MergedActivity':
      return 'Aktivität (Zusammengeführt)';
    case 'MergedContactPoint':
      return 'Kontaktpunkt (Zusammengeführt)';
    case 'MergedDistribution':
      return 'Verteilung (Zusammengeführt)';
    case 'MergedOrganization':
      return 'Organisation (Zusammengeführt)';
    case 'MergedOrganizationalUnit':
      return 'Organisationseinheit (Zusammengeführt)';
    case 'MergedPerson':
      return 'Person (Zusammengeführt)';
    case 'MergedPrimarySource':
      return 'Primäre Quelle (Zusammengeführt)';
    case 'MergedResource':
      return 'Resource (Zusammengeführt)';
    case 'MergedVariable':
      return 'Variable (Zusammengeführt)';
    case 'MergedVariableGroup':
      return 'Variablengruppe (Zusammengeführt)';
    default:
      return `Unbekannte zusammengeführte Entität (${value})`;
  }
}
