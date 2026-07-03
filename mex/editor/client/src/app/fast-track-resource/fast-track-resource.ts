import { Component, signal } from "@angular/core";
import { form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatFormField, MatLabel, MatError, MatInput } from "@angular/material/input";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import type { SearchContact } from "../services/contact-search";
import { ContactList } from "./contact-list/contact-list";
import type { CreateContact } from "./create-contact";
import { MatButton } from "@angular/material/button";

interface FastTrackResourceModel {
  title: string;
  contacts: (CreateContact | SearchContact | string)[];
}
@Component({
  selector: "mex-fast-track-resource",
  imports: [
    FormField,
    MatFormField,
    MatLabel,
    MatError,
    MatButton,
    MatInput,
    MatError,
    FormRoot,
    MatAutocompleteModule,
    ContactList,
  ],
  templateUrl: "./fast-track-resource.html",
  styleUrl: "./fast-track-resource.scss",
})
export class FastTrackResource {
  model = signal<FastTrackResourceModel>({
    title: "",
    contacts: [""],
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
  });

  deleteContact(index: number) {
    this.model.update((m) => {
      return { ...m, contacts: m.contacts.filter((_, i) => i !== index) };
    });
  }

  addContact() {
    this.model.update((m) => {
      return { ...m, contacts: [...m.contacts, ""] };
    });
  }

  onSubmit($event: SubmitEvent) {
    // eslint-disable-next-line no-console
    console.log("Submitted", $event, this.model());
  }
}
