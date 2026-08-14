import { Component, effect, input, linkedSignal, model } from "@angular/core";
import { form, FormField, FormRoot, required } from "@angular/forms/signals";
import { MatInput } from "@angular/material/input";
import { MatFormField } from "@angular/material/select";

import type { CreatePerson } from "../../../shared/models/create-item";
import { Fieldset } from "../../fieldset/fieldset";

@Component({
  selector: "mex-create-person-form",
  imports: [Fieldset, FormField, FormRoot, MatFormField, MatInput],
  templateUrl: "./create-person-form.html",
  styleUrl: "./create-person-form.scss",
})
/**
 * Form based component to create a {@link CreatePerson}.
 */
export class CreatePersonForm {
  readonly data = model<CreatePerson>();
  readonly inputText = input<string>();
  readonly isValid = model<boolean>();

  protected readonly formModel = linkedSignal<CreatePerson>(
    () => this.data() ?? this.createEmptyCreatePerson(this.inputText() ?? ""),
  );

  protected readonly personForm = form(this.formModel, (schema) => {
    required(schema.givenName);
    required(schema.familyName);
  });

  constructor() {
    effect(() => {
      const pForm = this.personForm();
      this.isValid.set(pForm.valid());
      this.data.set(pForm.value());
    });
  }

  private createEmptyCreatePerson(inputText: string): CreatePerson {
    let givenName = "";
    let familyName = "";
    if (inputText) {
      const [first, ...rest] = inputText.split(" ");
      givenName = first;
      familyName = rest.join(" ");
    }
    return {
      $type: "CreatePerson",
      givenName,
      familyName,
    };
  }
}
