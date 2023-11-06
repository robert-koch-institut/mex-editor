import { Component, EventEmitter, Input, OnChanges, OnDestroy, Output, SimpleChanges } from '@angular/core';
import { FormGroup, AbstractControl, FormArray, ValidationErrors } from '@angular/forms';
import { FormlyFormOptions, FormlyFieldConfig } from '@ngx-formly/core';
import * as _ from 'lodash-es';
import { Entity } from 'src/app/models/entity';
import { JSONSchema7 } from 'json-schema';
import { FormlyFieldConfigBuilderService } from 'src/app/services/formly-field-config-builder.service';
import { nameOf } from 'src/app/util/name-of';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-entity-edit-form',
  templateUrl: './entity-edit-form.component.html',
  styleUrls: ['./entity-edit-form.component.scss'],
})
export class EntityEditFormComponent implements OnChanges, OnDestroy {
  @Input() schema?: JSONSchema7;
  @Input() entity?: Entity;
  @Output() entityChanged = new EventEmitter<{
    entity?: Entity;
    valid: boolean;
  }>();

  form = new FormGroup({});
  options: FormlyFormOptions = {};
  fields: FormlyFieldConfig[] = [];
  model?: Entity;
  formSub: Subscription;

  constructor(private _formlyConfigBuilder: FormlyFieldConfigBuilderService) {
    this.formSub = this.form.valueChanges.subscribe(() =>
      this.entityChanged.emit({ entity: this.model, valid: this.form.valid })
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (nameOf<EntityEditFormComponent>('schema') in changes) {
      this.fields = this.schema ? [this._formlyConfigBuilder.build(this.schema)] : [];
    }
    if (nameOf<EntityEditFormComponent>('entity') in changes) {
      this.model = _.cloneDeep(this.entity);
    }
  }

  ngOnDestroy(): void {
    this.formSub.unsubscribe();
  }

  reset() {
    if (this.options.resetModel) {
      this.options.resetModel();
    }
  }

  getFormErrors(form: AbstractControl) {
    // onSubmitClick() {
    //   this.onSubmit.emit(this.model);
    if (form instanceof FormGroup || form instanceof FormArray) {
      const groupErrors = form.errors;
      // Form group can contain errors itself, in that case add'em
      const formErrors: { [key: string]: ValidationErrors } = groupErrors ? { groupErrors } : {};
      Object.keys(form.controls).forEach((key) => {
        // Recursive call of the FormGroup fields
        const subForm = form.get(key);

        if (subForm) {
          const error = this.getFormErrors(subForm);

          if (!_.isNil(error)) {
            // Only add error if not null
            formErrors[key] = error;
          }
        }
      });
      // Return FormGroup errors or null
      return Object.keys(formErrors).length > 0 ? formErrors : null;
    }

    return null;
  }
}
