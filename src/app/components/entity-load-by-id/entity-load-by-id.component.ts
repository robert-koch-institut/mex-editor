import { Component, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges } from '@angular/core';
import { AbstractControl, FormControl, ValidationErrors, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable, Subscription, catchError, combineLatest, map, of } from 'rxjs';
import { MergedEntity } from 'src/app/models/merged-entity';
import { EntityLoaderService } from 'src/app/services/entity-loader.service';
import { nameOf } from 'src/app/util/name-of';

@Component({
  selector: 'app-entity-load-by-id',
  templateUrl: './entity-load-by-id.component.html',
  styleUrls: ['./entity-load-by-id.component.scss'],
})
export class EntityLoadByIdComponent implements OnChanges, OnDestroy {
  @Input() stableTargetId = '';

  formControl = new FormControl('', [Validators.required], [(x) => this._validateStableTargetId(x)]);

  entity?: MergedEntity | undefined = undefined;
  @Output() entityChanged = new EventEmitter<MergedEntity | undefined>();
  private _valueChangeSub: Subscription;

  constructor(private _entityLoader: EntityLoaderService, private _snack: MatSnackBar) {
    this._valueChangeSub = combineLatest([this.formControl.statusChanges, this.formControl.valueChanges]).subscribe(
      ([state, value]) => {
        if (state === 'VALID' && value) {
          this._loadEntity(value);
        } else {
          this._setEntity(undefined);
        }
      }
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<EntityLoadByIdComponent>('stableTargetId') in changes) {
      this.formControl.patchValue(this.stableTargetId);
    }
  }

  ngOnDestroy(): void {
    this._valueChangeSub.unsubscribe();
  }

  private _setEntity(entity?: MergedEntity | undefined) {
    if (this.entity !== entity) {
      this.entity = entity;
      this.entityChanged.emit(this.entity);
    }
  }

  private _loadEntity(id: string | null) {
    if (id) {
      const sub = this._entityLoader
        .loadMergedEntity(id)
        .pipe(
          catchError(() => {
            this._snack.open(`Fehler beim Laden der Entität mit der Id '${id}'.`, undefined, { panelClass: 'bg-warn' });
            return of(undefined);
          })
        )
        .subscribe((x) => {
          this._setEntity(x);
          setTimeout(() => sub.unsubscribe());
        });
    } else {
      this._setEntity(undefined);
    }
  }

  private _validateStableTargetId(control: AbstractControl): Observable<ValidationErrors | null> {
    return this._entityLoader.loadMergedEntity(control.value).pipe(
      map(() => {
        return null;
      }),
      catchError(() => of({ invalidId: true }))
    );
  }
}
