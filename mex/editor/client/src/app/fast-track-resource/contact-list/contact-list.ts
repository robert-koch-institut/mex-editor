import { Component, computed, inject, model, output } from "@angular/core";
import type { SearchContact } from "../../services/contact-search";
import { ContactSearch } from "../../services/contact-search";
import { MatFormField, MatInput, MatInputModule, MatLabel } from "@angular/material/input";
import { MatIconModule } from "@angular/material/icon";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
// import type { FieldTree } from "@angular/forms/signals";
import { FormField, type FormValueControl } from "@angular/forms/signals";
import { FormsModule } from "@angular/forms";
import { MatChipsModule } from "@angular/material/chips";
import { MatButtonModule } from "@angular/material/button";
import { MatFormFieldModule } from "@angular/material/form-field";
import type { CreateContact } from "../create-contact";
import { MatDialog } from "@angular/material/dialog";
import { CreateContactDialog } from "../create-contact-dialog/create-contact-dialog";

@Component({
  selector: "mex-contact-list",
  imports: [
    MatFormField,
    MatLabel,
    MatIconModule,
    MatAutocompleteModule,
    MatInput,
    FormsModule,
    MatChipsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: "./contact-list.html",
  styleUrl: "./contact-list.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
export class ContactList implements FormValueControl<CreateContact | SearchContact | string> {
  private readonly searchService = inject(ContactSearch);
  private readonly dialog = inject(MatDialog);

  // readonly formField = input.required<FieldTree<SearchEntity | string>>();

  // ── Signal Forms contract ─────────────────────────────────────
  // FormValueControl requires `value` to be a model() signal.
  // [formField] will bind the parent form field's value to this.
  readonly value = model<CreateContact | SearchContact | string>("");

  // Signals the blur event so debounce('blur') works in schema.
  readonly touch = output<void>();

  // Optional state inputs (FormUiControl) — add as needed:
  // readonly disabled = input<boolean>(false);
  // readonly invalid  = input<boolean>(false);
  // readonly errors   = input<readonly ValidationError[]>([]);

  // ── Filter state (local, not in form model) ───────────────────
  readonly showPersons = model<boolean>(true);
  readonly showOrgs = model<boolean>(true);

  // ── Derived search results — pure computed, no subscription ───
  readonly searchResults = computed(() => {
    const v = this.value();
    let query = "";
    if (typeof v === "string") {
      query = v;
    } else if (typeof v === "object") {
      if ("label" in v) {
        query = v.label;
      } else {
        return [];
      }
    }
    return this.searchService.search(query, { persons: this.showPersons(), mail: this.showOrgs() });
  });

  openDialog(): void {
    const dialogRef = this.dialog.open(CreateContactDialog, {
      data: { selectedTab: this.showOrgs() ? "person" : "mail", searchValue: this.value() },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.value.set(result);
      }
    });
  }

  displayFn(entity: CreateContact | SearchContact | string | null): string {
    if (!entity) return "";
    if (typeof entity === "string") return entity;
    if ("$createtype" in entity) {
      if (entity.$createtype === "person") {
        return `⭐${entity.firstname} ${entity.lastname}`;
      }
      return `⭐${entity.email}`;
    }
    return entity.label;
  }
}
