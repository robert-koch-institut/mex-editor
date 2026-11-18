import { Component, computed, signal } from "@angular/core";
import type { Field } from "@angular/forms/signals";
import { form, FormField, FormRoot, validateStandardSchema } from "@angular/forms/signals";

import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import { Fieldset } from "../../shared/fieldset/fieldset";
import type { AccessRestriction } from "../../shared/models/generated/resource";
import { ZodFieldEditor } from "../../shared/zod-field-editor/zod-field-editor";
import { groupConf } from "../field-group-config";
import type { CreateResourceModel } from "./create-resource.model";
import { CreateResourceModelSchema } from "./create-resource.model";

/**
 * ResourceFieldTree API documentation.
 */
export type CreateResourceFieldTree = Field<CreateResourceModel[keyof CreateResourceModel]>;

/**
 * FieldGroupEntry API documentation.
 */
export interface FieldGroupEntry {
  key: keyof CreateResourceModel;
  field: CreateResourceFieldTree;
  schema: (typeof CreateResourceModelSchema.shape)[keyof typeof CreateResourceModelSchema.shape];
}

/**
 * FieldGroup API documentation.
 */
export interface FieldGroup {
  groupName: string;
  fields: FieldGroupEntry[];
}

@Component({
  imports: [FieldCategoryPipe, Fieldset, FormField, FormRoot, ZodFieldEditor],
  selector: "mex-create-resource",
  styleUrl: "./create-resource.scss",
  templateUrl: "./create-resource.html",
})
/**
 * Component to create a Resource with all fields.
 */
export class CreateResource {
  model = signal<CreateResourceModel>({
    accessRestriction: null as unknown as AccessRestriction,
    accrualPeriodicity: null,
    created: "",
    doi: "",
    hasPersonalData: null,
    license: null,
    maxTypicalAge: null,
    minTypicalAge: null,
    modified: "",
    numberOfRecords: null,
    numberOfUniqueIndividuals: null,
    sizeOfDataBasis: "",
    temporal: "",
    wasGeneratedBy: "",
    contact: [],
    theme: [],
    title: [],
    unitInCharge: [],
    accessPlatform: [],
    alternativeTitle: [],
    analytics: [],
    anonymizationPseudonymization: [],
    conformsTo: [],
    contributingUnit: [],
    contributor: [],
    creator: [],
    description: [],
    distribution: [],
    documentation: [],
    end: [],
    externalPartner: [],
    hasCodeValues: [],
    hasLegalBasis: [],
    hasPurpose: [],
    healthCategory: [],
    icd10code: [],
    instrumentToolOrApparatus: [],
    isPartOf: [],
    keyword: [],
    language: [],
    loincId: [],
    meshId: [],
    method: [],
    methodDescription: [],
    populationCoverage: [],
    provenance: [],
    publication: [],
    publisher: [],
    qualityInformation: [],
    relatedResource: [],
    resourceCreationMethod: [],
    resourceTypeGeneral: [],
    resourceTypeSpecific: [],
    rights: [],
    sample: [],
    source: [],
    spatial: [],
    start: [],
    stateOfDataProcessing: [],
  });

  resourceForm = form(
    this.model,
    (schema) => {
      validateStandardSchema(schema, CreateResourceModelSchema);
    },
    {
      submission: {
        action: async (_field) => {
          console.log("submit", this.model());
        },
        onInvalid: (field) => {
          const firstError = field().errorSummary()[0];
          firstError?.fieldTree().focusBoundControl();
        },
        ignoreValidators: "all",
      },
    },
  );
  protected readonly groups = computed<FieldGroup[]>(() => {
    const grouped = new Map<string, FieldGroupEntry[]>();

    // Get strictly typed keys from your model
    const keys = Object.keys(this.model()) as (keyof CreateResourceModel)[];

    for (const key of keys) {
      const groupName =
        groupConf.resource.categories.find((x) => x.properties.includes(key))?.id ?? "other";

      const field = this.resourceForm[key] as CreateResourceFieldTree;
      const entries = grouped.get(groupName) ?? [];
      entries.push({ key, field, schema: CreateResourceModelSchema.shape[key] });
      grouped.set(groupName, entries);
    }

    return Array.from(grouped, ([groupName, fields]) => ({
      groupName,
      fields,
    }));
  });
}
