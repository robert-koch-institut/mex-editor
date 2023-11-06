import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  OkCancelDialogComponent,
  OkCancelDialogConfig,
} from '../components/ok-cancel-dialog/ok-cancel-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class DialogService {
  constructor(private _dialog: MatDialog) {}

  showOkCancelDialog(config: OkCancelDialogConfig) {
    const ref = this._dialog.open<OkCancelDialogComponent, OkCancelDialogConfig, boolean>(OkCancelDialogComponent, {
      data: config,
      autoFocus: true,
      width: '',
      height: '',
    });
    return ref.afterClosed();
  }
}
