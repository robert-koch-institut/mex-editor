import { ChangeDetectorRef, OnDestroy, Pipe, PipeTransform } from '@angular/core';
import { Subscription } from 'rxjs';
import { EntityLoaderService } from '../services/entity-loader.service';
import { MergedEntity } from '../models/merged-entity';

export interface LoadMergedEntitySuccessResult {
  data: MergedEntity;
  state: 'success';
}

export interface LoadMergedEntityPendingResult {
  state: 'pending';
}

export interface LoadMergedEntityErrorResult {
  error: unknown;
  state: 'error';
}

export type LoadEntityResult =
  | LoadMergedEntitySuccessResult
  | LoadMergedEntityPendingResult
  | LoadMergedEntityErrorResult;

@Pipe({
  name: 'loadEntity',
  pure: false,
})
export class LoadEntityPipe implements PipeTransform, OnDestroy {
  private _ref: ChangeDetectorRef;
  private _latestValue: LoadEntityResult = { state: 'pending' };
  private _subscription: Subscription | null = null;
  private _stableTargetId: string | null = null;

  constructor(ref: ChangeDetectorRef, private entityLoader: EntityLoaderService) {
    this._ref = ref;
  }

  ngOnDestroy(): void {
    this._dispose();
  }

  transform(stableTargetId: string): LoadEntityResult {
    if (!this._stableTargetId) {
      if (stableTargetId) {
        this._stableTargetId = stableTargetId;
        this._subscription = this.entityLoader.loadMergedEntity(stableTargetId).subscribe({
          next: (x) => {
            this._latestValue = { data: x, state: 'success' };
            this._ref.markForCheck();
          },
          error: (error) => {
            this._latestValue = { error, state: 'error' };
            this._ref.markForCheck();
          },
        });
      }

      return this._latestValue;
    }

    if (stableTargetId !== this._stableTargetId) {
      this._dispose();
      return this.transform(stableTargetId);
    }

    return this._latestValue;
  }

  private _dispose(): void {
    this._subscription?.unsubscribe();
    this._subscription = null;
    this._latestValue = { state: 'pending' };
    this._stableTargetId = null;
  }
}
