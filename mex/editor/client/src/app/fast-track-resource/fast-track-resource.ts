import { Component, computed, inject, signal } from "@angular/core";
import { toObservable, toSignal } from "@angular/core/rxjs-interop";
import { form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatAutocomplete, MatAutocompleteTrigger } from "@angular/material/autocomplete";
import { MatChipGrid, MatChipRow, MatChipRemove, MatChipInput } from "@angular/material/chips";
import { MatIcon } from "@angular/material/icon";
import { MatFormField, MatLabel, MatError, MatInput } from "@angular/material/input";
import { MatSelect, MatOption } from "@angular/material/select";
import { debounceTime } from "rxjs";

import { BackendSearchService } from "../backend-search/backend-search.service";
import type { UnitOption } from "../backend-search/backend-search.types";
import { VocabularyService } from "../vocabulary/vocabulary.service";
import { MatButton } from "@angular/material/button";

import type { FastTrackResourceModel } from "./fast-track-resource.types";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    FormField,
    FormRoot,
    MatAutocomplete,
    MatAutocompleteTrigger,
    MatButton,
    MatChipGrid,
    MatChipInput,
    MatChipRemove,
    MatChipRow,
    MatError,
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
export class FastTrackResource {
  private vocabularyService = inject(VocabularyService);
  private search = inject(BackendSearchService);

  model = signal<FastTrackResourceModel>({
    title: "",
    theme: [],
    resourceCreationMethod: [],
    accrualPeriodicity: null,
    accessRestriction: "",
    unitInCharge: [],
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    minLength(schema.theme, 1, { message: "At least one theme is required" });
    required(schema.accessRestriction, { message: "Access restriction is required" });
    required(schema.unitInCharge, { message: "Need a unit in charge" });
  });

  theme = this.vocabularyService.getVocabulary("theme");

  themeOptions = computed(() => this.vocabularyService.toOptions(this.theme.value().items));

  resourceCreationMethod = this.vocabularyService.getVocabulary("resource-creation-method");

  resourceCreationMethodOptions = computed(() =>
    this.vocabularyService.toOptions(this.resourceCreationMethod.value().items),
  );

  accrualPeriodicity = this.vocabularyService.getVocabulary("frequency");

  accrualPeriodicityOptions = computed(() =>
    this.vocabularyService.toOptions(this.accrualPeriodicity.value().items),
  );

  accessRestriction = this.vocabularyService.getVocabulary("access-restriction");

  accessRestrictionOptions = computed(() =>
    this.vocabularyService.toOptions(this.accessRestriction.value().items),
  );

  /** Raw search input for the "unit in charge" field, debounced before it hits the backend. */
  unitInChargeQuery = signal("");

  private unitInChargeQueryDebounced = toSignal(
    toObservable(this.unitInChargeQuery).pipe(debounceTime(250)),
    { initialValue: "" },
  );

  unitInChargeUnits = this.search.searchUnits(this.unitInChargeQueryDebounced);

  unitInChargeOptions = computed(() => this.search.toOptions(this.unitInChargeUnits.value().items));

  /** Caches labels for selected unit ids so chips can render names, not identifiers. */
  private unitLabels = new Map<string, string>();

  unitLabel(id: string): string {
    return this.unitLabels.get(id) ?? id;
  }

  addUnit(option: UnitOption) {
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

  onSubmit() {
    // eslint-disable-next-line no-console
    console.log("Submitted", this.model());
  }
}
