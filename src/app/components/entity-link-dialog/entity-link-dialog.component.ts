import { AfterViewInit, Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { isString } from 'lodash-es';
import { delay, catchError, map, of } from 'rxjs';
import { MergedEntity } from 'src/app/models/merged-entity';
import { EntityLinkService } from 'src/app/services/entity-link.service';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';
import { MergedEntitySearchComponent } from '../merged-entity-search/merged-entity-search.component';

export interface EntityLinkDialogData {
  source: MergedEntity | string;
}

@Component({
  selector: 'app-entity-link-dialog',
  templateUrl: './entity-link-dialog.component.html',
  styleUrls: ['./entity-link-dialog.component.scss'],
})
export class EntityLinkDialogComponent implements OnInit, AfterViewInit {
  leftEntity?: MergedEntity;
  rightEntity?: MergedEntity;
  linkingEntities = false;

  @ViewChild(MergedEntitySearchComponent) entitySearch?: MergedEntitySearchComponent;

  constructor(
    public dialogRef: MatDialogRef<EntityLinkDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EntityLinkDialogData,
    private _snack: MatSnackBar,
    private _entityLoader: EntityLoaderService,
    private _entityLinker: EntityLinkService
  ) {}

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (this.entitySearch) {
        this.entitySearch.search();
      }
    });
  }

  ngOnInit(): void {
    this._ensureLeftEntity();
  }

  linkEntities() {
    if (!!this.leftEntity && !!this.rightEntity) {
      this.linkingEntities = true;
      this.dialogRef.disableClose = true;

      const left = this.leftEntity;
      const right = this.rightEntity;

      const sub = this._entityLinker
        .linkEntities(left, right)
        .pipe(
          delay(200000),
          map(() => 'success' as const),
          catchError(() => {
            this._snack.open(
              `Fehler beim Zusammenführen der Entitäten (${left.stableTargetId}, ${right.stableTargetId}).`,
              undefined,
              { panelClass: 'bg-warn' }
            );
            return of('error' as const);
          })
        )
        .subscribe((x) => {
          this.linkingEntities = false;
          this.dialogRef.disableClose = false;

          if (x === 'success') {
            this.dialogRef.close();
          }
          setTimeout(() => sub.unsubscribe());
        });
    }
  }

  private _ensureLeftEntity() {
    if (isString(this.data.source)) {
      const sub = this._entityLoader
        .loadMergedEntity(this.data.source)
        .pipe(
          catchError(() => {
            this._snack.open(`Fehler beim Laden einer Entität mit der Id '${this.data.source}'.`, undefined, {
              panelClass: 'bg-warn',
            });
            return of(undefined);
          })
        )
        .subscribe((x) => {
          this.leftEntity = x;
          setTimeout(() => sub.unsubscribe());
        });
    } else {
      this.leftEntity = this.data.source;
    }
  }
}
