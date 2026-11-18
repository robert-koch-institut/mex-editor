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
import { LinkEditor } from "../link-editor/link-editor";
import { asLinkLanguage } from "../models";
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
import type { ResolvedSchema } from "./zod-type-resolve";
import { innerOf, WRAPPERS } from "./zod-type-resolve";

function objectEntries(schema: z.ZodType): { key: string; schema: z.ZodType }[] {
  const shape = (schema as z.ZodObject).shape as Record<string, z.ZodType>;
  return Object.entries(shape).map(([key, child]) => ({ key, schema: child }));
}

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
  readonly label = input<string>("Feld");
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
        // entries: objectEntries(unwrapped),
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
