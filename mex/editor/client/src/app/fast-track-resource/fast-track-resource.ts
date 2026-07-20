import { Component, computed, inject, signal } from "@angular/core";
import { toObservable, toSignal } from "@angular/core/rxjs-interop";
import { form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatAutocomplete, MatAutocompleteTrigger } from "@angular/material/autocomplete";
import { MatChipGrid, MatChipRow, MatChipRemove, MatChipInput } from "@angular/material/chips";
import { MatIcon } from "@angular/material/icon";
import { MatFormField, MatLabel, MatError, MatInput } from "@angular/material/input";
import { MatSelect, MatOption } from "@angular/material/select";
import { debounceTime } from "rxjs";

import { BackendProxy } from "../shared/backend-proxy.service";
import { VocabularySearch } from "./vocabulary-search.service";
import { MatButton } from "@angular/material/button";

import type { FastTrackResourceModel } from "./fast-track-resource.types";

import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { ContactList } from "./contact-list/contact-list";
import { ResourceSubmission } from "./resource-submission";
import type { Text } from "../shared/models/text";
import type { Concept } from "./vocabulary-search.types";
import type { PreviewOrganizationalUnit } from "../shared/models";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    ContactList,
    FormField,
    FormRoot,
    MatAutocomplete,
    MatAutocompleteModule,
    MatAutocompleteTrigger,
    MatButton,
    MatChipGrid,
    MatChipInput,
    MatChipRemove,
    MatChipRow,
    MatError,
    MatFormField,
    MatIcon,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
  ],
  templateUrl: "./fast-track-resource.html",
  styleUrl: "./fast-track-resource.scss",
})
/**
 * Page to create a resource the fast way.
 */
export class FastTrackResource {
  private resourceSubmissionService = inject(ResourceSubmission);
  private vocabularySearchService = inject(VocabularySearch);
  private search = inject(BackendProxy);

  model = signal<FastTrackResourceModel>({
    title: "",
    theme: [],
    resourceCreationMethod: [],
    accrualPeriodicity: null,
    accessRestriction: "",
    unitInCharge: [],
    contacts: [""],
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    minLength(schema.theme, 1, { message: "At least one theme is required" });
    required(schema.accessRestriction, { message: "Access restriction is required" });
    required(schema.unitInCharge, { message: "Need a unit in charge" });
  });

  private vocabularyItemsAsOptions(name: string) {
    const vocab = this.vocabularySearchService.getVocabulary(name);
    return computed(() => FastTrackResource.toOptions(vocab.value().items));
  }

  themeOptions = this.vocabularyItemsAsOptions("theme");
  resourceCreationMethodOptions = this.vocabularyItemsAsOptions("resource-creation-method");
  accrualPeriodicityOptions = this.vocabularyItemsAsOptions("frequency");
  accessRestrictionOptions = this.vocabularyItemsAsOptions("access-restriction");

  /** Raw search input for the "unit in charge" field, debounced before it hits the backend. */
  unitInChargeQuery = signal("");

  private unitInChargeQueryDebounced = toSignal(
    toObservable(this.unitInChargeQuery).pipe(debounceTime(250)),
    { initialValue: "" },
  );

  unitInChargeUnits = this.search.searchUnits(this.unitInChargeQueryDebounced);

  unitInChargeOptions = computed(() =>
    FastTrackResource.toOptions(this.unitInChargeUnits.value().items),
  );

  /** Caches labels for selected unit ids so chips can render names, not identifiers. */
  private unitLabels = new Map<string, string>();

  /** Map concepts to selectable options, preferring the German label. */
  static toOptions(
    concepts: Concept[] | PreviewOrganizationalUnit[],
  ): { id: string; label: string }[] {
    return concepts.map((concept) => {
      if ("$type" in concept) {
        const displayName = (name: Text[]): string => {
          const german = name.find((text) => text.language === "de");
          return german?.value ?? name[0]?.value ?? "";
        };
        return { id: concept.identifier, label: displayName(concept.name) || concept.identifier };
      }
      return {
        id: concept.identifier,
        label: concept.prefLabel.de ?? concept.prefLabel.en ?? concept.identifier,
      };
    });
  }

  unitLabel(id: string): string {
    return this.unitLabels.get(id) ?? id;
  }

  addUnit(option: { id: string; label: string }) {
    this.unitLabels.set(option.id, option.label);
    this.model.update((model) =>
      model.unitInCharge.includes(option.id)
        ? model
        : { ...model, unitInCharge: [...model.unitInCharge, option.id] },
    );
    this.unitInChargeQuery.set("");
  }

  removeUnit(id: string) {
    this.model.update((model) => ({
      ...model,
      unitInCharge: model.unitInCharge.filter((unitId) => unitId !== id),
    }));
  }

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

  onSubmit() {
    this.resourceSubmissionService.submit(this.model).subscribe((result) => {
      // eslint-disable-next-line no-console
      console.log("Submitted", this.model(), result.stableTargetId);
    });
  }
}
