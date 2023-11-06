import { Pipe, PipeTransform } from '@angular/core';
import { EntityType, isEntityType, mapLabel } from '../models/entity-type';
import { MergedEntityType, mapLabel as mapMergedLabel } from '../models/merged-entity-type';

@Pipe({
  name: 'entityTypeLabel',
})
export class EntityTypeLabelPipe implements PipeTransform {
  transform(value: EntityType | MergedEntityType): string {
    if (isEntityType(value)) {
      return mapLabel(value);
    }
    return mapMergedLabel(value);
  }
}
