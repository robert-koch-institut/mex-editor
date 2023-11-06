import { Component } from '@angular/core';
import { FieldArrayType } from '@ngx-formly/core';
import * as _ from 'lodash-es';
import { DialogService } from 'src/app/services/dialog.service';

@Component({
  selector: 'app-array-formly-field-type',
  templateUrl: './array-formly-field-type.component.html',
  styleUrls: ['./array-formly-field-type.component.scss'],
})
export class ArrayFormlyFieldTypeComponent extends FieldArrayType {
  constructor(private _dialogService: DialogService) {
    super();
  }

  override remove(i: number, a?: { markAsDirty: boolean } | undefined): void {
    const performRemove = () => {
      super.remove(i, a);
    };

    if (this._hasContent(i)) {
      const confirm$ = this._dialogService.showOkCancelDialog({
        title: 'Element wirklich löschen?',
        message: 'Sind Sie sicher, dass Sie dieses Element löschen wollen?',
        icon: 'delete',
        ok: { label: 'Löschen', color: 'warn' },
      });
      confirm$.subscribe((x) => {
        if (x === true) {
          performRemove();
        }
      });
    } else {
      performRemove();
    }
  }

  private _hasContent(index: number): boolean {
    if (Array.isArray(this.formControl.value)) {
      const array = this.formControl.value;
      const value = array.at(index);

      if (_.isArray(value) || _.isObject(value)) {
        return _.some(value, (x) => !_.isEmpty(x));
      }

      return !_.isEmpty(value);
    }

    return false;
  }
}
