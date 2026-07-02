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
    resourceTypeGeneral: [],
    resourceCreationMethod: [],
    accrualPeriodicity: null,
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
  });

  resourceTypeGeneral = this.vocabularyService.getVocabulary("resource-type-general");

  resourceTypeGeneralOptions = computed(() =>
    this.vocabularyService.toOptions(this.resourceTypeGeneral.value().items),
  );

  resourceCreationMethod = this.vocabularyService.getVocabulary("resource-creation-method");

  resourceCreationMethodOptions = computed(() =>
    this.vocabularyService.toOptions(this.resourceCreationMethod.value().items),
  );

  accrualPeriodicity = this.vocabularyService.getVocabulary("frequency");

  accrualPeriodicityOptions = computed(() =>
    this.vocabularyService.toOptions(this.accrualPeriodicity.value().items),
  );

  onSubmit() {
    // eslint-disable-next-line no-console
    console.log("Submitted", this.model());
  }
}
