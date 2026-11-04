import { CommonModule } from "@angular/common";
import { Component, inject, signal } from "@angular/core";
import { MatButton } from "@angular/material/button";
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from "@angular/material/dialog";
import { MatTabsModule } from "@angular/material/tabs";
import { TranslocoPipe } from "@jsverse/transloco";

import type {
  CreateContactPoint,
  CreateOrganization,
  CreatePerson,
} from "../../shared/models/create-item";
import { CreateContactPointForm } from "./create-contact-point-form/create-contact-point-form";
import { CreateOrganizationForm } from "./create-organization-form/create-organization-form";
import { CreatePersonForm } from "./create-person-form/create-person-form";

/**
 * Model to pass data to {@link CreateItemDialog}.
 */
export interface CreateItemDialogData {
  initialSelectedTab?: "Person" | "ContactPoint" | "Organization";
  allowedTypes?: ("Person" | "ContactPoint" | "Organization")[];
  inputText?: string;
}

/**
 * Model for the form data collected by {@link CreateItemDialog}.
 */
export interface CreateItemFormData {
  isValid: boolean;
  data: CreatePerson | CreateContactPoint | CreateOrganization;
}

/**
 * Model for result of {@link CreateItemDialog}.
 */
export type CreateItemDialogResult = CreatePerson | CreateContactPoint | CreateOrganization | null;

@Component({
  selector: "mex-create-item-dialog",
  imports: [
    CommonModule,
    CreateContactPointForm,
    CreateOrganizationForm,
    CreatePersonForm,
    MatButton,
    MatDialogModule,
    MatTabsModule,
    TranslocoPipe,
  ],
  templateUrl: "./create-item-dialog.html",
  styleUrl: "./create-item-dialog.scss",
  host: {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    "(keydown.enter)": "closeDialogIfValidData()",
  },
})
/**
 * Dialog to create items. Supported items are {@link CreatePerson}, {@link CreateContactPoint}
 */
export class CreateItemDialog {
  private dialogRef = inject(MatDialogRef);
  readonly personTab = {
    $type: "Person" as const,
    data: undefined as CreatePerson | undefined,
    isValid: false,
  };
  readonly contactPointTab = {
    $type: "ContactPoint" as const,
    data: undefined as CreateContactPoint | undefined,
    isValid: false,
  };
  readonly organizationTab = {
    $type: "Organization" as const,
    data: undefined as CreateOrganization | undefined,
    isValid: false,
  };

  private readonly _tabs = [this.personTab, this.contactPointTab, this.organizationTab];

  readonly data = inject<CreateItemDialogData>(MAT_DIALOG_DATA);

  readonly tabs = signal(
    this._tabs.filter((x) =>
      (this.data.allowedTypes ?? this._tabs.map((t) => t.$type)).includes(x.$type),
    ),
  );
  readonly formData = signal<CreateItemFormData | null>(null);

  selectedTabIndex = signal(
    this.tabs().findIndex(
      (x) => x.$type == (this.data.initialSelectedTab ?? this.data.allowedTypes?.at(0) ?? "Person"),
    ),
  );

  closeDialogIfValidData() {
    const selectedTabContent = this.tabs()[this.selectedTabIndex()];
    if (selectedTabContent.isValid) {
      this.dialogRef.close(selectedTabContent.data);
    }
  }
}
