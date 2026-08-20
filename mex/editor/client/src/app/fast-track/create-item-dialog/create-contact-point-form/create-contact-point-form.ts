import { Component, effect, input, linkedSignal, model } from "@angular/core";
import { email, form, FormField, FormRoot, required } from "@angular/forms/signals";
import { MatInput } from "@angular/material/input";
import { MatFormField } from "@angular/material/select";

import type { CreateContactPoint } from "../../../shared/models/create-item";
import { Fieldset } from "../../fieldset/fieldset";

@Component({
  selector: "mex-create-contact-point-form",
  imports: [Fieldset, FormField, FormRoot, MatFormField, MatInput],
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

  protected readonly contactPointForm = form(this.formModel, (schema) => {
    required(schema.email);
    email(schema.email);
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
