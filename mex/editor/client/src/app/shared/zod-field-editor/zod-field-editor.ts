import { JsonPipe } from "@angular/common";
import type { Signal } from "@angular/core";
import { ElementRef } from "@angular/core";
import {
  Component,
  computed,
  forwardRef,
  inject,
  input,
  model,
  output,
  signal,
  viewChild,
} from "@angular/core";
import type { Field, FormValueControl } from "@angular/forms/signals";
import { FormField } from "@angular/forms/signals";
import { MatIcon } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatOption, MatPrefix, MatSelect } from "@angular/material/select";
import { translateSignal, TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { ZodObject } from "zod";
import { z } from "zod";
import { $ZodCheckRegex } from "zod/v4/core";

import {
  ArrayFormValueControl,
  ArrayItemTemplate,
} from "../array-form-value-control/array-form-value-control";
import type {
  ConceptLookup,
  LinkLanguageLookup,
  NoneLookup,
  TextLanguageLookup,
} from "../concept-lookups.service";
import { ConceptLookups } from "../concept-lookups.service";
import type { DatepickerPrecision } from "../datepicker/datepicker";
import { Datepicker } from "../datepicker/datepicker";
import { FieldErrors } from "../field-errors/field-errors";
import { readFieldMetadata } from "../field-metadata.pipe";
import { LinkEditor } from "../link-editor/link-editor";
import { MexErrorStateMatcher } from "../mex-error-state-matcher";
import type { PreviewItem } from "../models";
import type { CreateItem } from "../models/create-item";
import { ActivityTypeSchema } from "../models/generated/activity";
import {
  AccessRestrictionSchema,
  AnonymizationPseudonymizationSchema,
  DataProcessingStateSchema,
  FrequencySchema,
  HealthCategorySchema,
  LanguageSchema,
  LicenseSchema,
  PersonalDataSchema,
  PurposeSchema,
  ResourceCreationMethodSchema,
  ResourceTypeGeneralSchema,
} from "../models/generated/resource";
import type { Link, Text } from "../models/generated/shared";
import {
  LinkLanguageSchema,
  LinkSchema,
  TextLanguageSchema,
  TextSchema,
  ThemeSchema,
  yearMonthDayPattern,
  yearMonthDayTimePattern,
  yearMonthPattern,
  yearPattern,
} from "../models/generated/shared";
import type { ReferenceType } from "../models/zod-reference";
import { ReferenceSelect } from "../reference-select/reference-select";
import { TextEditor } from "../text-editor/text-editor";
import { createEmptyValue, unwrapDetailed } from "../zod-util";
import { ZodObjectEditor } from "./zod-object-editor/zod-object-editor";

interface EnumLookup {
  label: string;
  value: unknown;
}
type Lookup = ConceptLookup | LinkLanguageLookup | TextLanguageLookup | NoneLookup | EnumLookup;

interface BaseResolvedSchema<T> {
  readonly schema: z.ZodType;
  readonly unwrappedSchema: z.ZodType;
  readonly zodType: string;
  readonly optional: boolean;
  readonly nullable: boolean;
  readonly formField: Field<T>;
}
/**
 * Resolved schema for enums.
 */
export interface ResolvedEnumSchema extends BaseResolvedSchema<string> {
  $type: "enum";
  options: Signal<Lookup[]>;
}

/**
 * Resolved schema for enums arrays.
 */
export interface ResolvedEnumArraySchema extends BaseResolvedSchema<string[]> {
  $type: "enum-array";
  options: Signal<Lookup[]>;
}

/**
 * Resolved schema for string.
 */
export interface ResolvedStringSchema extends BaseResolvedSchema<string> {
  $type: "string";
}

/**
 * Resolved schema for number.
 */
export interface ResolvedNumberSchema extends BaseResolvedSchema<number> {
  $type: "number";
}

/**
 * Resolved schema for link.
 */
export interface ResolvedLinkSchema extends BaseResolvedSchema<Link> {
  $type: "link";
}

/**
 * Resolved schema for text.
 */
export interface ResolvedTextSchema extends BaseResolvedSchema<Text> {
  $type: "text";
}

/**
 * Resolved schema for object.
 */
export interface ResolvedObjectSchema<T extends ZodObject = ZodObject> extends BaseResolvedSchema<
  z.infer<T>
> {
  $type: "object";
  objectSchema: T;
}

/**
 * Resolved schema for unions.
 */
export interface ResolvedUnionSchema extends BaseResolvedSchema<unknown> {
  $type: "union";
  schemaOptions: readonly z.ZodType[];
}

/**
 * Resolved schema for arrays.
 */
export interface ResolvedArraySchema extends BaseResolvedSchema<unknown[]> {
  $type: "array";
  elementSchema: z.ZodType;
  createNewItem: () => unknown;
}

/**
 * Resolved schema datetime strings.
 */
export interface ResolvedDateSchema extends BaseResolvedSchema<string | null> {
  $type: "date";
  allowedPrecisions: readonly DatepickerPrecision[];
}

/**
 * Resolved schema for reference.
 */
export interface ResolvedReferenceSchema extends BaseResolvedSchema<PreviewItem | CreateItem> {
  $type: "reference";
  allowedTypes: ReferenceType[];
}

/**
 * Resolved schema for reference arrays.
 */
export interface ResolvedReferenceArraySchema extends BaseResolvedSchema<
  (PreviewItem | CreateItem)[]
> {
  $type: "reference-array";
  allowedTypes: ReferenceType[];
}

/**
 * Resolved schema for types that are not known yet/can't be handled.
 */
export interface ResolvedUnknownSchema extends Omit<BaseResolvedSchema<unknown>, "formField"> {
  $type: "unknown";
}

/**
 * Resolved schema for zod-types. Used as interface for the components internal behaviour, representing all schemas that the component is able to serve/render.
 */
export type ResolvedSchema =
  | ResolvedEnumSchema
  | ResolvedEnumArraySchema
  | ResolvedArraySchema
  | ResolvedDateSchema
  | ResolvedStringSchema
  | ResolvedNumberSchema
  | ResolvedReferenceSchema
  | ResolvedUnionSchema
  | ResolvedReferenceArraySchema
  | ResolvedLinkSchema
  | ResolvedTextSchema
  | ResolvedObjectSchema
  | ResolvedUnknownSchema;

/** Maps the source of each date regex to the matching datepicker precision. */
const PRECISION_BY_PATTERN_SOURCE = new Map<string, DatepickerPrecision>([
  [yearMonthDayTimePattern, "datetime"],
  [yearMonthDayPattern, "day"],
  [yearMonthPattern, "month"],
  [yearPattern, "year"],
]);

function getZodRegExString<T>(value: T): string | null {
  return (
    (value instanceof z.ZodString &&
      value.def.checks?.length === 1 &&
      value.def.checks[0] instanceof $ZodCheckRegex &&
      value.def.checks[0]._zod.def.pattern.source) ||
    null
  );
}

/**
 * Returns the precisions of a union, if ALL options are date strings.
 */
function datePrecisionsOfUnion(schema: z.ZodUnion): DatepickerPrecision[] | null {
  const precisions: DatepickerPrecision[] = [];
  for (const option of schema.options) {
    const regEx = getZodRegExString(option);
    const precision = regEx ? PRECISION_BY_PATTERN_SOURCE.get(regEx) : undefined;
    if (!precision) return null;

    precisions.push(precision);
  }
  return precisions;
}

@Component({
  selector: "mex-zod-field-editor",
  imports: [
    ArrayFormValueControl,
    ArrayItemTemplate,
    Datepicker,
    FieldErrors,
    FormField,
    forwardRef(() => ZodObjectEditor),
    JsonPipe,
    LinkEditor,
    MatFormField,
    MatIcon,
    MatInput,
    MatOption,
    MatPrefix,
    MatSelect,
    ReferenceSelect,
    TextEditor,
    TranslocoPipe,
  ],
  templateUrl: "./zod-field-editor.html",
  styleUrl: "./zod-field-editor.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
/**
 * ZodFieldEditor API documentation.
 */
export class ZodFieldEditor<T extends z.ZodType> implements FormValueControl<z.infer<T>> {
  readonly schema = input.required<T>();
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly touched = input(false);

  /** Form value; kept in sync with the bound field by `[formField]`. */
  readonly value = model.required<z.infer<T>>();
  /** Emitted when the user leaves an input; lets `[formField]` mark the outer field as touched. */
  readonly touch = output<void>();

  protected readonly errorMatcher = new MexErrorStateMatcher();

  protected readonly activeFocusContol = viewChild<
    FormValueControl<unknown> | ElementRef<HTMLElement>
  >("focusControl");

  focus() {
    const target = this.activeFocusContol();
    if (target) {
      if (target instanceof ElementRef) {
        target.nativeElement.focus();
      } else if (target.focus) {
        target.focus();
      }
    }
  }

  private readonly formField = inject(FormField<z.infer<T>>);
  readonly resolvedSchema = computed(() => {
    return this.resolveSchema(this.schema(), this.formField);
  });

  private readonly transloco = inject(TranslocoService);
  readonly selectNoneLabel = translateSignal("select.none-option");
  readonly lookups = inject(ConceptLookups);
  private lookupMapping = new Map<z.ZodEnum, Signal<Lookup[]>>([
    [ThemeSchema, this.lookups.themeOptions],
    [AccessRestrictionSchema, this.lookups.accessRestrictionOptions],
    [FrequencySchema, this.lookups.frequencyOptions],
    [PersonalDataSchema, this.lookups.personalDataOptions],
    [LicenseSchema, this.lookups.licenseOptions],
    [AnonymizationPseudonymizationSchema, this.lookups.anonymizationPseudonymizationOptions],
    [ResourceCreationMethodSchema, this.lookups.resourceCreationMethodOptions],
    [LanguageSchema, this.lookups.languageOptions],
    [ResourceTypeGeneralSchema, this.lookups.resourceTypeGeneralOptions],
    [PurposeSchema, this.lookups.purposeOptions],
    [HealthCategorySchema, this.lookups.healthCategoryOptions],
    [DataProcessingStateSchema, this.lookups.dataProcessingStateOptions],
    [ActivityTypeSchema, this.lookups.activityTypeOptions],
    [TextLanguageSchema, this.lookups.textLanguageOptions],
    [LinkLanguageSchema, this.lookups.linkLanguageOptions],
  ]);

  private getLookup(
    enumType: z.ZodEnum,
    lookupConfig?: { optional: boolean; nullable: boolean },
  ): Signal<Lookup[]> {
    if (this.lookupMapping.has(enumType)) {
      const mapping = this.lookupMapping.get(enumType)!;
      if (lookupConfig && (lookupConfig.nullable || lookupConfig.optional)) {
        return computed(() => {
          const emptyOption: NoneLookup<null | undefined> = {
            value: lookupConfig.nullable ? null : undefined,
            label: this.selectNoneLabel(),
            data: lookupConfig.nullable ? null : undefined,
          };
          const inner = mapping();
          return [emptyOption, ...inner];
        });
      }
      return mapping;
    }

    return signal(
      Object.entries(enumType.def.entries).map(([label, value]) => {
        return { label, value, data: value };
      }),
    );
  }

  // eslint-disable-next-line complexity, max-lines-per-function
  protected resolveSchema(schema: T, formField: FormField<z.infer<T>>): ResolvedSchema {
    const { unwrapped, optional, nullable } = unwrapDetailed(schema);
    const zodType = unwrapped.def.type as string;
    const baseResult = {
      zodType,
      optional,
      nullable,
      schema,
      unwrappedSchema: unwrapped,
    };

    const referenceTypes = schema.meta()?.referenceTypes;
    if (referenceTypes) {
      if (unwrapped instanceof z.ZodArray) {
        return {
          ...baseResult,
          $type: "reference-array",
          formField: formField.field() as Field<(CreateItem | PreviewItem)[]>,
          allowedTypes: referenceTypes,
        };
      }
      return {
        ...baseResult,
        $type: "reference",
        formField: formField.field() as Field<CreateItem | PreviewItem>,
        allowedTypes: referenceTypes,
      };
    }

    if (unwrapped instanceof z.ZodUnion) {
      const allowedPrecisions = datePrecisionsOfUnion(unwrapped);
      if (allowedPrecisions) {
        return {
          ...baseResult,
          $type: "date",
          formField: formField.field() as Field<string | null>,
          allowedPrecisions,
        };
      }

      return {
        ...baseResult,
        $type: "union",
        formField: formField.field() as Field<unknown>,
        schemaOptions: unwrapped.options as z.ZodType[],
      };
    }

    if (unwrapped instanceof z.ZodObject) {
      if (unwrapped === LinkSchema) {
        return { ...baseResult, $type: "link", formField: formField.field() as Field<Link> };
      }
      if (unwrapped === TextSchema) {
        return { ...baseResult, $type: "text", formField: formField.field() as Field<Text> };
      }

      return {
        ...baseResult,
        $type: "object",
        formField: formField.field() as Field<z.infer<ZodObject>>,
        objectSchema: unwrapped,
      };
    }
    if (unwrapped instanceof z.ZodArray) {
      const elementSchema = unwrapped.element as z.ZodType;
      const unwrappedElementResult = unwrapDetailed(elementSchema);

      if (unwrappedElementResult.unwrapped instanceof z.ZodEnum) {
        return {
          ...baseResult,
          $type: "enum-array",
          formField: formField.field() as Field<string[]>,
          options: this.getLookup(unwrappedElementResult.unwrapped, unwrappedElementResult),
        };
      }
      return {
        ...baseResult,
        $type: "array",
        formField: formField.field() as Field<unknown[]>,
        elementSchema: elementSchema,
        createNewItem: () => createEmptyValue(elementSchema, this.transloco.activeLang),
      };
    }

    if (unwrapped instanceof z.ZodEnum) {
      return {
        ...baseResult,
        $type: "enum",
        formField: formField.field() as Field<string>,
        options: this.getLookup(unwrapped, baseResult),
      };
    }

    if (unwrapped instanceof z.ZodNumber) {
      return {
        ...baseResult,
        $type: "number",
        formField: formField.field() as Field<number>,
      };
    }

    if (unwrapped instanceof z.ZodString) {
      const regEx = getZodRegExString(unwrapped);
      if (regEx) {
        // eslint-disable-next-line no-console
        console.log(
          "Found Regex",
          readFieldMetadata(formField.field(), "labelKey"),
          regEx,
          "resolve to formatted-text",
        );
      }

      return {
        ...baseResult,
        $type: "string",
        formField: formField.field() as Field<string>,
      };
    }

    return {
      ...baseResult,
      $type: "unknown",
    };
  }
}
