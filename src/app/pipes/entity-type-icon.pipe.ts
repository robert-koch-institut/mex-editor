import { Pipe, PipeTransform } from '@angular/core';
import { EntityType } from '../models/entity-type';
import { MergedEntityType } from '../models/merged-entity-type';

@Pipe({
  name: 'entityTypeIcon',
})
export class EntityTypeIconPipe implements PipeTransform {
  transform(value: EntityType | MergedEntityType): string {
    switch (value) {
      case 'AccessPlatform':
      case 'MergedAccessPlatform':
        return 'garage_home';
      case 'Activity':
      case 'MergedActivity':
        return 'rebase';
      case 'ContactPoint':
      case 'MergedContactPoint':
        return 'contact_mail';
      case 'Person':
      case 'MergedPerson':
        return 'person';
      case 'Distribution':
      case 'MergedDistribution':
        return 'crowdsource';
      case 'Resource':
      case 'MergedResource':
        return 'home_storage';
      case 'Organization':
      case 'MergedOrganization':
        return 'account_tree';
      case 'OrganizationalUnit':
      case 'MergedOrganizationalUnit':
        return 'rectangle';
      case 'PrimarySource':
      case 'MergedPrimarySource':
        return 'database';
      case 'Variable':
      case 'MergedVariable':
        return 'fiber_manual_record';
      case 'VariableGroup':
      case 'MergedVariableGroup':
        return 'workspaces';
      default:
        return 'question_mark';
    }
  }
}
