import { Component, OnInit } from '@angular/core';
import { FieldType, FieldTypeConfig } from '@ngx-formly/core';
import * as _ from 'lodash-es';

@Component({
  selector: 'app-object-formly-field-type',
  templateUrl: './object-formly-field-type.component.html',
  styleUrls: ['./object-formly-field-type.component.scss'],
})
export class ObjectFormlyFieldTypeComponent extends FieldType<FieldTypeConfig> implements OnInit {
  useRowLayout = false;

  ngOnInit(): void {
    this.useRowLayout = this.determineUseRowLayout();
  }

  determineUseRowLayout() {
    if (this.field.fieldGroup) {
      if (_.some(this.field.fieldGroup, (x) => _.includes(['array', 'object'], x.type))) {
        return false;
      }
      return this.field.fieldGroup.length <= 3;
    }
    return true;
  }
}
