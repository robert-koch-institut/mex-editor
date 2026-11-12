import { Component, effect, input, linkedSignal, model } from "@angular/core";
import { form, FormField, FormRoot, validateStandardSchema } from "@angular/forms/signals";
import { MatInput } from "@angular/material/input";
import { MatFormField } from "@angular/material/select";

import { FieldCategoryPipe } from "../../../shared/field-category-pipe";
import type { CreateOrganization } from "../../../shared/models/create-item";
import { CreateOrganizationSchema } from "../../../shared/models/create-item";
import { Fieldset } from "../../fieldset/fieldset";

@Component({
  selector: "mex-create-organization-form",
  imports: [FieldCategoryPipe, Fieldset, FormField, FormRoot, MatFormField, MatInput],
  templateUrl: "./create-organization-form.html",
  styleUrl: "./create-organization-form.scss",
})
/**
 * Form based component to create a {@link CreateOrganization}.
 */
export class CreateOrganizationForm {
  readonly data = model<CreateOrganization>();
  readonly inputText = input<string>();
  readonly isValid = model<boolean>();

  protected readonly formModel = linkedSignal<CreateOrganization>(
    () => this.data() ?? this.createEmptyCreateOrganization(this.inputText() ?? ""),
  );
  protected readonly organizationSchema = CreateOrganizationSchema;
  protected readonly organizationForm = form(this.formModel, (schema) => {
    validateStandardSchema(schema, CreateOrganizationSchema);
  });

  constructor() {
    effect(() => {
      const pForm = this.organizationForm();
      this.isValid.set(pForm.valid());
      this.data.set(pForm.value());
    });
  }

  private createEmptyCreateOrganization(inputText: string): CreateOrganization {
    return {
      $type: "CreateOrganization",
      officialName: inputText,
    };
  }
}
