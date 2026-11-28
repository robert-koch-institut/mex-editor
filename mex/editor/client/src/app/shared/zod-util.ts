/* eslint-disable complexity */

import type { Signal } from "@angular/core";
import z from "zod";

import { asLinkLanguage, asTextLanguage } from "./models";
import type { Link, Text } from "./models/generated/shared";
import { LinkSchema, TextSchema } from "./models/generated/shared";

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

/**
 * Unwraps the given schema and checks for nullable and/or optional wrappers.
 * @param schema The given schema to unwrap.
 * @returns The unwrapped schema including nullable and optional infos.
 */
export function unwrapDetailed(schema: z.ZodType) {
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

/**
 * Creates an empty value for the given zod schema.
 * @param schema The schema to create an empty value for.
 * @returns The empty value for the given schema.
 */
export function createEmptyValue(
  schema: z.ZodType,
  currentLanguage: Signal<string>,
  recursiveCall: typeof createEmptyValue = createEmptyValue,
): unknown {
  const type = schema.def.type as string;

  if (type === "optional") {
    return undefined;
  }

  if (type === "nullable" || type === "null") {
    return null;
  }

  if (type === "default" || type === "prefault") {
    const parsed = schema.safeParse(undefined);
    return parsed.success
      ? parsed.data
      : recursiveCall(innerOf(schema), currentLanguage, recursiveCall);
  }

  if (type === "readonly" || type === "nonoptional") {
    return recursiveCall(innerOf(schema), currentLanguage, recursiveCall);
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
    return recursiveCall(schema.options.at(0) as z.ZodType, currentLanguage, recursiveCall);
  }

  if (type === "array") {
    return [];
  }

  if (type === "object") {
    if (schema === (LinkSchema as unknown)) {
      const emptyLink: Link = {
        url: "",
        language: asLinkLanguage(currentLanguage()),
      };
      return emptyLink;
    }

    if (schema === (TextSchema as unknown)) {
      const emptyText: Text = {
        value: "",
        language: asTextLanguage(currentLanguage()),
      };
      return emptyText;
    }

    return Object.fromEntries(
      objectEntries(schema).map(({ key, schema: child }) => [
        key,
        recursiveCall(child, currentLanguage, recursiveCall),
      ]),
    );
  }

  return undefined;
}

/**
 * Creates an empty form value for the given zod schema.
 * It ensures no undefined in form values since they lead to undefined fields.
 * @param schema The schema to create an empty form value for.
 * @returns The empty form value for the given schema.
 */
export function createEmptyFormValue<T extends z.ZodType>(
  schema: T,
  currentLanguage: Signal<string>,
): z.infer<T> {
  const unwrapped = unwrapDetailed(schema);
  if (unwrapped.unwrapped instanceof z.ZodArray) {
    return [] as z.infer<T>;
  }
  if (unwrapped.unwrapped instanceof z.ZodString) {
    return "" as z.infer<T>;
  }
  if (unwrapped.optional || unwrapped.nullable) {
    return null as z.infer<T>;
  }

  return createEmptyValue(schema, currentLanguage, createEmptyFormValue) as z.infer<T>;
}
