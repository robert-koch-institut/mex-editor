import type { Signal } from "@angular/core";
import type { Field } from "@angular/forms/signals";
import type z from "zod";

import type { Lookup } from "../../shared/concept-lookups.service";
import type { Link, Text } from "../../shared/models/generated/shared";

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

/** Entfernt optional/nullable/default/... bis zum eigentlichen Typ (zod 4: def.type / def.innerType). */
export function unwrapZod(schema: z.ZodType): z.ZodType {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let s: any = schema;
  while (WRAPPERS.has(s.def.type)) s = s.def.innerType;
  return s;
}

/** Return the innerType of the given zod-type. */
export function innerOf(schema: z.ZodType): z.ZodType {
  return (schema.def as unknown as { innerType: z.ZodType }).innerType;
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
  $type: "enum" | "enum-array";
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
export interface ResolvedObjectSchema extends BaseResolvedSchema<object> {
  $type: "object";
  entries: { key: string; schema: z.ZodType }[];
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
