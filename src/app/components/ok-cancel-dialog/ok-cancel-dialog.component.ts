import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

export interface OkCancelDialogButtonConfig {
  label: string;
  color?: string;
}

export interface OkCancelDialogConfig {
  title: string;
  message: string;
  icon?: string;
  ok?: OkCancelDialogButtonConfig;
  cancel?: OkCancelDialogButtonConfig;
}

@Component({
  selector: 'app-ok-cancel-dialog',
  templateUrl: './ok-cancel-dialog.component.html',
  styleUrls: ['./ok-cancel-dialog.component.scss'],
})
export class OkCancelDialogComponent {
  get message() {
    return this.config?.message ?? 'Ok oder abbrechen?';
  }

  get title() {
    return this.config?.title ?? 'Titel';
  }

  get okConfig() {
    return { label: 'Ok', ...this.config?.ok };
  }

  get cancelConfig() {
    return { label: 'Abbrechen', ...this.config?.cancel };
  }

  constructor(@Inject(MAT_DIALOG_DATA) public config: OkCancelDialogConfig) {}
}
