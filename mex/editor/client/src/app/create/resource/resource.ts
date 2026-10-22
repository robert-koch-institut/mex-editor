import { Component, computed, signal } from "@angular/core";
import type { FieldTree } from "@angular/forms/signals";
import { FormRoot } from "@angular/forms/signals";
import { form, validateStandardSchema } from "@angular/forms/signals";
import type z from "zod";

import type { AccessRestriction } from "../../shared/models/generated/resource";
import {
  BaseResourceSchema,
  ExtractedResourceSchema,
} from "../../shared/models/generated/resource";
import { recommended } from "../../shared/models/zod-types";
import { ZodFieldEditor } from "../../shared/zod-field-editor/zod-field-editor";
import { groupConf } from "./groupconf";

// eslint-disable-next-line @typescript-eslint/naming-convention
const CreateResourceSchema = BaseResourceSchema.extend({
  creator: recommended(ExtractedResourceSchema.shape.creator),
  contributor: recommended(ExtractedResourceSchema.shape.contributor),
  contributingUnit: recommended(ExtractedResourceSchema.shape.contributingUnit),
  healthCategory: recommended(ExtractedResourceSchema.shape.healthCategory),
  temporal: recommended(ExtractedResourceSchema.shape.temporal),
  spatial: recommended(ExtractedResourceSchema.shape.spatial),
  hasLegalBasis: recommended(ExtractedResourceSchema.shape.hasLegalBasis),
});

type CreateResource = z.infer<typeof CreateResourceSchema>;

@Component({
  selector: "mex-create-resource",
  imports: [FormRoot, ZodFieldEditor],
  templateUrl: "./resource.html",
  styleUrl: "./resource.scss",
})

/**
 * Resource API documentation.
 */
export class Resource {
  model = signal<CreateResource>({
    accessRestriction: null as unknown as AccessRestriction,
    accrualPeriodicity: null,
    created: "",
    doi: null,
    hasPersonalData: null,
    license: null,
    maxTypicalAge: null,
    minTypicalAge: null,
    modified: "",
    numberOfRecords: null,
    numberOfUniqueIndividuals: null,
    sizeOfDataBasis: null,
    temporal: "",
    wasGeneratedBy: null,
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  shape: any = CreateResourceSchema.shape;

  resourceForm = form(
    this.model,
    (schema) => {
      validateStandardSchema(schema, CreateResourceSchema);
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

  /** Gruppenname -> (Feldname -> FieldTree) */
  protected readonly groups = computed(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = new Map<string, Map<string, FieldTree<any>>>();
    for (const key of Object.keys(CreateResourceSchema.shape)) {
      const group =
        groupConf.resource.categories.find((x) => x.properties.includes(key))?.id ?? "other";
      if (!result.has(group)) result.set(group, new Map());
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      result.get(group)!.set(key, (this.resourceForm as any)[key]);
    }
    return result;
  });
}
