import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { MergedEntity } from 'src/app/models/merged-entity';
import { nameOf } from 'src/app/util/name-of';

@Component({
  selector: 'app-merged-entity-list',
  templateUrl: './merged-entity-list.component.html',
  styleUrls: ['./merged-entity-list.component.scss'],
})
export class MergedEntityListComponent implements OnChanges {
  @Input() entities?: MergedEntity[];

  @Input() selectedEntity?: MergedEntity;
  @Output() selectedEntityChanged = new EventEmitter<MergedEntity | undefined>();

  @Input() enableNavigation = true;
  @Input() enableSelection = true;

  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<MergedEntityListComponent>('entities') in changes) {
      this.setSelectedEntity(undefined);
    }
  }

  trackEntity(index: number, item: MergedEntity) {
    return item.identifier;
  }

  selectEntity(entity: MergedEntity) {
    if (this.enableSelection) {
      this.setSelectedEntity(entity);
    }
  }

  private setSelectedEntity(entity?: MergedEntity | undefined) {
    if (this.selectedEntity !== entity) {
      this.selectedEntity = entity;
      this.selectedEntityChanged.emit(this.selectedEntity);
    }
  }
}
