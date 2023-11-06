import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EntityRuleSet, NewEntityRuleSetForEntities } from 'src/app/models/entity-rule-set';

export interface RuleSetSaveDialogData {
  ruleSet: EntityRuleSet | NewEntityRuleSetForEntities;
}

export interface RuleSetSaveDialogResult {
  result: 'save' | 'cancel';
}

@Component({
  selector: 'app-rule-set-save-dialog',
  templateUrl: './rule-set-save-dialog.component.html',
  styleUrls: ['./rule-set-save-dialog.component.scss'],
})
export class RuleSetSaveDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: RuleSetSaveDialogData) {}
}
