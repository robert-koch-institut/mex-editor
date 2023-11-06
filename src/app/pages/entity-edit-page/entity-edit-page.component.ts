import { Component, OnDestroy, OnInit } from '@angular/core';
import { of, Subscription, switchMap } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { EntityRuleSet, NewEntityRuleSet, isNewEntityRuleSet } from 'src/app/models/entity-rule-set';
import * as _ from 'lodash-es';
import {
  RuleSetSaveDialogComponent,
  RuleSetSaveDialogData,
  RuleSetSaveDialogResult,
} from 'src/app/components/rule-set-save-dialog/rule-set-save-dialog.component';
import { EntityRuleSetSaverService } from 'src/app/services/entity-rule-set-saver.service';
import { EntityEdit, EntityEditService } from 'src/app/services/entity-edit.service';
import {
  EntityLinkDialogComponent,
  EntityLinkDialogData,
} from 'src/app/components/entity-link-dialog/entity-link-dialog.component';

@Component({
  selector: 'app-entity-edit-page',
  templateUrl: './entity-edit-page.component.html',
  styleUrls: ['./entity-edit-page.component.scss'],
})
export class EntityEditPageComponent implements OnInit, OnDestroy {
  isSaving = false;

  ruleSetEdit?: EntityEdit;
  ruleSetEditSub?: Subscription;
  initialRuleSet?: EntityRuleSet | NewEntityRuleSet | undefined;

  constructor(
    private route: ActivatedRoute,
    private _entityEditService: EntityEditService,
    private ruleSetSaver: EntityRuleSetSaverService,
    private _dialog: MatDialog,
    private _router: Router
  ) {}

  ngOnInit(): void {
    this.ruleSetEditSub = this.route.paramMap
      .pipe(
        switchMap((x) => {
          const stableTargetId = x.has('stableTargetId') && x.get('stableTargetId');
          return stableTargetId ? this._entityEditService.loadEntityEdit(stableTargetId) : of(undefined);
        })
      )
      .subscribe((x) => {
        this.ruleSetEdit = x;
        this.initialRuleSet = _.cloneDeep(x?.ruleSet);
      });
  }

  ngOnDestroy(): void {
    this.ruleSetEditSub?.unsubscribe();
  }

  linkEntity() {
    if (this.ruleSetEdit) {
      this._dialog.open<EntityLinkDialogComponent, EntityLinkDialogData>(EntityLinkDialogComponent, {
        data: { source: this.ruleSetEdit.stableTargetId },
      });
    }
  }

  reset() {
    if (this.initialRuleSet) {
      this.ruleSetEdit = {
        ...(this.ruleSetEdit || { entities: [], schema: {}, stableTargetId: '' }),
        ruleSet: _.cloneDeep(this.initialRuleSet),
      };
      console.log('EntityEditPageComponent :: reset()', this.ruleSetEdit);
    }
  }

  showPreview() {
    if (this.ruleSetEdit) {
      const ruleSet = this.ruleSetEdit.ruleSet;
      const data: RuleSetSaveDialogData = isNewEntityRuleSet(ruleSet)
        ? { ruleSet: { ruleSet: ruleSet, stableTargetId: this.ruleSetEdit.stableTargetId } }
        : { ruleSet };
      this._dialog
        .open<RuleSetSaveDialogComponent, RuleSetSaveDialogData, RuleSetSaveDialogResult>(RuleSetSaveDialogComponent, {
          data,
        })
        .afterClosed()
        .pipe(
          switchMap((x) => {
            if (x && x.result === 'save') {
              this.isSaving = true;
              return this.ruleSetSaver.save(data.ruleSet);
            }
            return of(undefined);
          })
        )
        .subscribe((x) => {
          if (x !== undefined && this.ruleSetEdit) {
            this.ruleSetEdit.ruleSet = x;
            this.initialRuleSet = _.cloneDeep(x);
          }
          this.isSaving = false;
        });
    }
  }
}
