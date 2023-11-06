import { nameOf } from '../util/name-of';
import { Entity } from './entity';
import { MergedEntityType } from './merged-entity-type';

export const metadataEditorPrimarySourceId = 'mex-editor';
export const uneditableEntityFields = [
  nameOf<Entity>('identifier'),
  nameOf<Entity>('stableTargetId'),
  nameOf<Entity>('hadPrimarySource'),
];
export const displayEntityFields: {
  [key in MergedEntityType]: { title: string; additionalFields?: string[] };
} = {
  MergedAccessPlatform: {
    title: 'title',
    additionalFields: ['alternativeTitle', 'unitInCharge'],
  },
  MergedActivity: {
    title: 'title',
    additionalFields: ['shortName', 'responsibleUnit', 'start', 'end'],
  },
  MergedContactPoint: {
    title: 'email',
  },
  MergedDistribution: {
    title: 'title',
  },
  MergedOrganization: {
    title: 'officialName',
    additionalFields: ['shortName', 'alternativeName'],
  },
  MergedOrganizationalUnit: {
    title: 'shortName',
  },
  MergedPerson: {
    title: 'fullName',
    additionalFields: ['memberOf'],
  },
  MergedPrimarySource: {
    title: 'title',
    additionalFields: ['unitInCharge', 'contact'],
  },
  MergedResource: {
    title: 'title',
    additionalFields: ['unitInCharge', 'wasGeneratedBy'],
  },
  MergedVariable: {
    title: 'label',
    additionalFields: ['belongsTo', 'usedIn'],
  },
  MergedVariableGroup: {
    title: 'label',
    additionalFields: ['containedBy'],
  },
};
