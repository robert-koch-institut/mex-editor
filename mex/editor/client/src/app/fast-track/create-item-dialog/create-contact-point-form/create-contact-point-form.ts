import { Component, effect, input, linkedSignal, model } from "@angular/core";
import { form, FormField, FormRoot, validateStandardSchema } from "@angular/forms/signals";
import { MatInput } from "@angular/material/input";
import { MatFormField } from "@angular/material/select";

import { FieldCategoryPipe } from "../../../shared/field-category-pipe";
import {
  type CreateContactPoint,
  CreateContactPointSchema,
} from "../../../shared/models/create-item";
import { Fieldset } from "../../fieldset/fieldset";

@Component({
  selector: "mex-create-contact-point-form",
  imports: [FieldCategoryPipe, Fieldset, FormField, FormRoot, MatFormField, MatInput],
  templateUrl: "./create-contact-point-form.html",
  styleUrl: "./create-contact-point-form.scss",
})
/**
 * Form based component to create a {@link CreateContactPoint}.
 */
export class CreateContactPointForm {
  readonly data = model<CreateContactPoint>();
  readonly inputText = input<string>();
  readonly isValid = model<boolean>();

  protected readonly formModel = linkedSignal<CreateContactPoint>(
    () => this.data() ?? this.createEmptyCreateContactPoint(this.inputText() ?? ""),
  );

  protected readonly contactPointSchema = CreateContactPointSchema;

  protected readonly contactPointForm = form(this.formModel, (schema) => {
    validateStandardSchema(schema, CreateContactPointSchema);
  });

  constructor() {
    effect(() => {
      const f = this.contactPointForm();
      this.data.set(f.value());
      this.isValid.set(f.valid());
    });
  }

  private createEmptyCreateContactPoint(inputText: string): CreateContactPoint {
    return {
      $type: "CreateContactPoint",
      email: inputText,
    };
  }
}
