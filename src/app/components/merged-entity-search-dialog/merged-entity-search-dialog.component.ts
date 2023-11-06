import { Component, Inject, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MergedEntity } from 'src/app/models/merged-entity';
import { MergedEntityType } from 'src/app/models/merged-entity-type';
import { DefaultPageSize, MergedEntitySearchComponent } from '../merged-entity-search/merged-entity-search.component';

export interface MergedEntitySearchDialogData {
  entityTypes: MergedEntityType[];
}

@Component({
  selector: 'app-merged-entity-search-dialog',
  templateUrl: './merged-entity-search-dialog.component.html',
  styleUrls: ['./merged-entity-search-dialog.component.scss'],
})
export class MergedEntitySearchDialogComponent {
  @ViewChild(MergedEntitySearchComponent) mergedEntitySearch?: MergedEntitySearchComponent;

  selectedEntity?: MergedEntity;
  entitySearch = {
    query: '',
    filter: { entityTypes: this.data.entityTypes },
    page: { index: 0, size: DefaultPageSize },
  };

  constructor(@Inject(MAT_DIALOG_DATA) public data: MergedEntitySearchDialogData) {}

  search(): void {
    if (this.mergedEntitySearch) {
      this.mergedEntitySearch.search();
    }
  }
}
