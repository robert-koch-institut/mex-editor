import { JsonPipe } from "@angular/common";
import type { Signal } from "@angular/core";
import {
  Component,
  computed,
  forwardRef,
  inject,
  input,
  model,
  output,
  signal,
} from "@angular/core";
import type { Field, FormValueControl } from "@angular/forms/signals";
import { FormField } from "@angular/forms/signals";
import { MatIcon } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatOption, MatPrefix, MatSelect } from "@angular/material/select";
import { translateSignal, TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { ZodObject } from "zod";
import { z } from "zod";

import {
  ArrayFormValueControl,
  ArrayItemTemplate,
} from "../array-form-value-control/array-form-value-control";
import type { Lookup, NoneLookup } from "../concept-lookups.service";
import { ConceptLookups } from "../concept-lookups.service";
import { Datepicker } from "../datepicker/datepicker";
import { FieldErrorSummary } from "../field-error-summary/field-error-summary";
import { FieldErrors } from "../field-errors/field-errors";
import { LinkEditor } from "../link-editor/link-editor";
import { asLinkLanguage, asTextLanguage } from "../models";
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
} from "../models/generated/shared";
import { TextEditor } from "../text-editor/text-editor";
import { ZodObjectEditor } from "./zod-object-editor/zod-object-editor";

/** Wrapper schemas that only decorate an inner schema and keep the editable shape. */
export const WRAPPERS = new Set([
  "optional",
  "nullable",
  "default",
  "prefault",
  "readonly",
  "catch",
  "nonoptional",
]);

/** Return the innerType of the given zod-type. */
export function innerOf(schema: z.ZodType): z.ZodType {
  return (schema.def as unknown as { innerType: z.ZodType }).innerType;
}

function objectEntries(schema: z.ZodType): { key: string; schema: z.ZodType }[] {
  const shape = (schema as z.ZodObject).shape as Record<string, z.ZodType>;
  return Object.entries(shape).map(([key, child]) => ({ key, schema: child }));
}

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
 * Resolved schema for arrays.
 */
export interface ResolvedArraySchema extends BaseResolvedSchema<unknown[]> {
  $type: "array";
  elementSchema: z.ZodType;
  createNewItem: () => unknown;
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
  | ResolvedStringSchema
  | ResolvedNumberSchema
  | ResolvedLinkSchema
  | ResolvedTextSchema
  | ResolvedObjectSchema
  | ResolvedUnknownSchema;

function unwrapDetailed(schema: z.ZodType) {
  let unwrapped: z.ZodType = schema;
  let optional = false;
  let nullable = false;

  while (WRAPPERS.has(unwrapped.def.type)) {
    if (unwrapped.def.type === "optional") optional = true;
    if (unwrapped.def.type === "nullable") nullable = true;
    unwrapped = innerOf(unwrapped);
  }

  return { unwrapped, optional, nullable };
}

@Component({
  selector: "mex-zod-field-editor",
  imports: [
    ArrayFormValueControl,
    ArrayItemTemplate,
    Datepicker,
    FieldErrors,
    FieldErrorSummary,
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

  /** Form value; kept in sync with the bound field by `[formField]`. */
  readonly value = model.required<z.infer<T>>();
  /** Emitted when the user leaves an input; lets `[formField]` mark the outer field as touched. */
  readonly touch = output<void>();

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

    console.log("NO ENUM LOOKUPS FOUND FOR", enumType);
    return signal([]);
  }

  // eslint-disable-next-line complexity
  protected createEmptyValue(schema: z.ZodType): unknown {
    const type = schema.def.type as string;
    if (type === "optional") {
      return undefined;
    }

    if (type === "nullable" || type === "null") {
      return null;
    }

    if (type === "default" || type === "prefault") {
      const parsed = schema.safeParse(undefined);
      return parsed.success ? parsed.data : this.createEmptyValue(innerOf(schema));
    }

    if (type === "readonly" || type === "nonoptional") {
      return this.createEmptyValue(innerOf(schema));
    }

    if (type === "string") {
      return "";
    }

    if (type === "number") {
      return NaN;
    }

    if (type === "boolean") {
      return false;
    }

    if (type === "enum" && schema instanceof z.ZodEnum) {
      return schema.options.at(0);
    }

    if (type === "literal" && schema instanceof z.ZodLiteral) {
      return schema.def.values.at(0);
    }

    if (type === "union" && schema instanceof z.ZodUnion) {
      return this.createEmptyValue(schema.options.at(0) as z.ZodType);
    }

    if (type === "array") {
      return [];
    }

    if (type === "object") {
      if (schema === LinkSchema) {
        const emptyLink: Link = {
          url: "",
          language: asLinkLanguage(this.transloco.getActiveLang()),
        };
        return emptyLink;
      }

      if (schema === TextSchema) {
        const emptyText: Text = {
          value: "",
          language: asTextLanguage(this.transloco.getActiveLang()),
        };
        return emptyText;
      }

      return Object.fromEntries(
        objectEntries(schema).map(({ key, schema: child }) => [key, this.createEmptyValue(child)]),
      );
    }

    return undefined;
  }

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

    if (unwrapped instanceof z.ZodObject) {
      if (unwrapped === LinkSchema) {
        return { ...baseResult, $type: "link", formField: formField.field() as Field<Link> };
      }
      if (unwrapped === TextSchema) {
        return { ...baseResult, $type: "text", formField: formField.field() as Field<Text> };
      }

      console.log("ITS AN OBJECT", unwrapped);

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
        createNewItem: () => this.createEmptyValue(elementSchema),
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
