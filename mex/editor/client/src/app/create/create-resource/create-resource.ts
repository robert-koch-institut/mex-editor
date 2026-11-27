import type { StepperSelectionEvent } from "@angular/cdk/stepper";
import type { Signal } from "@angular/core";
import { Component, computed, inject, input, signal } from "@angular/core";
import type { Field, ValidationError } from "@angular/forms/signals";
import {
  form,
  FormField,
  FormRoot,
  StandardSchemaValidationError,
  validateStandardSchema,
} from "@angular/forms/signals";
import { MatButton } from "@angular/material/button";
import { MatStepperModule } from "@angular/material/stepper";
import { ActivatedRoute, Router } from "@angular/router";
import { TranslocoDirective } from "@jsverse/transloco";

import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import { FieldError } from "../../shared/field-error/field-error";
import { addFieldLabelKeysAndDescriptionKeys } from "../../shared/field-metadata.pipe";
import { Fieldset } from "../../shared/fieldset/fieldset";
import type { AccessRestriction } from "../../shared/models/generated/resource";
import { ValidationErrorMessagePipe } from "../../shared/validation-error-message-pipe";
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
  errors: Signal<ValidationError.WithFieldTree[]>;
}

@Component({
  imports: [
    FieldCategoryPipe,
    FieldError,
    Fieldset,
    FormField,
    FormRoot,
    MatButton,
    MatStepperModule,
    TranslocoDirective,
    ValidationErrorMessagePipe,
    ZodFieldEditor,
  ],
  selector: "mex-create-resource",
  styleUrl: "./create-resource.scss",
  templateUrl: "./create-resource.html",
})

/**
 * Component to create a Resource with all fields.
 */
export class CreateResource {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

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
    instrumentToolOrApparatus: [{ value: "" }],
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
      addFieldLabelKeysAndDescriptionKeys(schema, CreateResourceModelSchema, "Resource");
    },
    {
      submission: {
        action: async (_field) => {
          // eslint-disable-next-line no-console
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

  readonly step = input<string>();
  readonly availableSteps = computed(() => {
    return [...this.groups().map((g) => g.groupName), "summary"];
  });

  readonly selectedIndex = computed(() => {
    const step = this.step();
    const index = this.availableSteps().findIndex((s) => s === step);
    return index === -1 ? 0 : index;
  });

  onStepChanged(event: StepperSelectionEvent, info: { isLastStep: boolean }) {
    if (info.isLastStep) {
      this.resourceForm().markAsTouched();
    }
    const stepName = this.availableSteps().at(event.selectedIndex);
    if (stepName) {
      this.router.navigate(["..", stepName], {
        relativeTo: this.route,
      });
    }
  }

  focusControl(error: ValidationError.WithFieldTree) {
    const tree = error.fieldTree();
    setTimeout(() => tree.focusBoundControl(), 250);
  }

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

    return Array.from(grouped, ([groupName, fields]) => createFieldGroups(groupName, fields)).sort(
      (a, b) => a.position - b.position,
    );
  });
}

function createFieldGroups(groupName: string, fields: FieldGroupEntry[]) {
  const errors = computed(() => {
    return fields
      .map((x) => {
        const state = x.field();
        return state.touched()
          ? state.errorSummary().map((error) => ({
              error,
              depth:
                error instanceof StandardSchemaValidationError
                  ? (error.issue.path?.length ?? 1)
                  : 1,
            }))
          : [];
      })
      .flat()
      .sort((a, b) => a.depth - b.depth)
      .map((x) => x.error);
  });
  return {
    groupName,
    fields,
    errors,
    position: groupConf.resource.categories.findIndex((c) => c.id === groupName),
  };
}
