import { Component, computed, inject, signal } from "@angular/core";
import { MAT_DIALOG_DATA, MatDialogModule } from "@angular/material/dialog";
import { MatTabsModule } from "@angular/material/tabs";
import { MatInputModule, MatLabel } from "@angular/material/input";
import { MatFormFieldModule } from "@angular/material/form-field";
import { FormsModule } from "@angular/forms";
import { email, form, FormField, FormRoot, required } from "@angular/forms/signals";
import type { CreateMail } from "../create-contact";
import { type CreatePerson } from "../create-contact";

export interface CreateContactDialogData {
  selectedTab?: "person" | "mail";
  searchValue: string;
}

@Component({
  selector: "mex-create-contact-dialog",
  imports: [
    MatDialogModule,
    MatTabsModule,
    MatLabel,
    MatFormFieldModule,
    FormsModule,
    FormRoot,
    FormField,
    MatInputModule,
  ],
  templateUrl: "./create-contact-dialog.html",
  styleUrl: "./create-contact-dialog.scss",
})
export class CreateContactDialog {
  readonly tabs = ["person", "mail"] as const;
  readonly data = inject<CreateContactDialogData>(MAT_DIALOG_DATA);
  selectedTabIndex = signal<number>(
    (this.data.selectedTab ?? "person" in this.tabs)
      ? this.tabs.indexOf(this.data.selectedTab ?? "person")
      : 0,
  );

  canClose = computed(() => {
    if (this.selectedTabIndex() === 0) {
      return this.personForm().valid();
    } else if (this.selectedTabIndex() === 1) {
      return this.mailForm().valid();
    }
    return false;
  });
  closeResult = computed(() => {
    if (this.selectedTabIndex() === 0) {
      return this.person();
    } else if (this.selectedTabIndex() === 1) {
      return this.mail();
    }
    return null;
  });

  createInitialPersonModel() {
    let firstname = "";
    let lastname = "";
    if (this.data.searchValue) {
      const [first, ...rest] = this.data.searchValue.split(" ");
      firstname = first;
      lastname = rest.join(" ");
    }
    return {
      $createtype: "person" as const,
      firstname: firstname,
      lastname: lastname,
    };
  }

  person = signal<CreatePerson>(this.createInitialPersonModel());
  personForm = form(this.person, (schema) => {
    required(schema.firstname);
    required(schema.lastname);
  });

  mail = signal<CreateMail>({
    $createtype: "mail",
    email: this.data.searchValue ?? "",
  });
  mailForm = form(this.mail, (schema) => {
    required(schema.email);
    email(schema.email);
  });
}
