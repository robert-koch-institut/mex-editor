import { Component, computed, inject, signal } from "@angular/core";
import { form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatFormField, MatLabel, MatError, MatInput } from "@angular/material/input";
import { MatSelect, MatOption } from "@angular/material/select";

import { VocabularyService } from "../vocabulary/vocabulary.service";
import { MatButton } from "@angular/material/button";

import type { FastTrackResourceModel } from "./fast-track-resource.types";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    FormField,
    FormRoot,
    MatButton,
    MatError,
    MatError,
    MatFormField,
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

  model = signal<FastTrackResourceModel>({
    title: "",
    theme: [],
    resourceCreationMethod: [],
    accrualPeriodicity: null,
    accessRestriction: "",
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    minLength(schema.theme, 1, { message: "At least one theme is required" });
    required(schema.accessRestriction, { message: "Access restriction is required" });
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

  onSubmit() {
    // eslint-disable-next-line no-console
    console.log("Submitted", this.model());
  }
}
