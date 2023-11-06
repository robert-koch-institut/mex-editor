import { AfterViewInit, Component, TemplateRef, Type, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { FieldTypeConfig, FormlyFieldConfig } from '@ngx-formly/core';
import { FieldType } from '@ngx-formly/material';
import { FormlyFieldProps } from '@ngx-formly/material/form-field';
import { EntityType } from 'src/app/models/entity-type';
import {
  MergedEntitySearchDialogComponent,
  MergedEntitySearchDialogData,
} from '../merged-entity-search-dialog/merged-entity-search-dialog.component';
import { MergedEntityType } from 'src/app/models/merged-entity-type';
import {
  Observable,
  catchError,
  delay,
  distinctUntilChanged,
  iif,
  map,
  of,
  shareReplay,
  startWith,
  switchMap,
  tap,
} from 'rxjs';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';
import { LoadEntityResult } from 'src/app/pipes/load-entity.pipe';
import { MergedEntity } from 'src/app/models/merged-entity';

interface EntityLookupProps extends FormlyFieldProps {
  lookupOptions: { entityTypes: EntityType[] };
}

export interface FormlyEntityLookupFieldConfig extends FormlyFieldConfig<EntityLookupProps> {
  type: 'entity-lookup' | Type<EntityLookupFormlyFieldTypeComponent>;
}

@Component({
  selector: 'app-entity-lookup-formly-field-type',
  templateUrl: './entity-lookup-formly-field-type.component.html',
  styleUrls: ['./entity-lookup-formly-field-type.component.scss'],
})
export class EntityLookupFormlyFieldTypeComponent
  extends FieldType<FieldTypeConfig<EntityLookupProps>>
  implements AfterViewInit
{
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  @ViewChild('suffixButton', { static: true }) suffixButton!: TemplateRef<any>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  @ViewChild('prefixButton', { static: true }) prefixButton!: TemplateRef<any>;

  entityLoad$?: Observable<LoadEntityResult | undefined>;
  hideInput = false;

  constructor(private _dialog: MatDialog, private _entityLoader: EntityLoaderService) {
    super();
  }

  ngAfterViewInit() {
    this.props.suffix = this.suffixButton;
    this.props.prefix = this.prefixButton;

    this.entityLoad$ = this.formControl.valueChanges.pipe(
      startWith(this.formControl.value),
      distinctUntilChanged(),
      switchMap((x) => {
        return iif(
          () => this.formControl.valid && x,
          this._entityLoader.loadMergedEntity(x).pipe(
            map((e) => {
              return { state: 'success' as const, data: e };
            }),
            delay(200000),
            catchError((err) => of({ state: 'error' as const, error: err })),
            startWith({ state: 'pending' as const })
          ),
          of(undefined)
        );
      }),
      tap((x) => (this.hideInput = x?.state === 'success')),
      shareReplay()
    );
  }

  searchEntity() {
    const dialogRef = this._dialog.open<MergedEntitySearchDialogComponent, MergedEntitySearchDialogData, MergedEntity>(
      MergedEntitySearchDialogComponent,
      {
        data: { entityTypes: this.props.lookupOptions.entityTypes.map((x) => `Merged${x}` as MergedEntityType) },
      }
    );
    dialogRef.afterOpened().subscribe((x) => dialogRef.componentInstance.search());
    dialogRef.afterClosed().subscribe((x) => {
      if (x) {
        this.formControl.patchValue(x.identifier);
      }
    });
  }
}
