import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { Field, FieldTree, SchemaPath, SchemaPathTree } from "@angular/forms/signals";
import { applyEach, createMetadataKey, metadata } from "@angular/forms/signals";
import type { z } from "zod";

const fieldLabelKeyMetadataKey = createMetadataKey<string>();
const fieldDescriptionKeyMetadataKey = createMetadataKey<string>();

type AnySchema = z.core.$ZodType;

interface SchemaDef {
  type: string;
  innerType?: AnySchema;
  element?: AnySchema;
  shape?: Record<string, AnySchema>;
}

const WRAPPER_TYPES = new Set([
  "optional",
  "nullable",
  "default",
  "prefault",
  "nonoptional",
  "readonly",
  "catch",
]);

function getDef(schema: AnySchema): SchemaDef {
  return schema._zod.def as unknown as SchemaDef;
}

function unwrap(schema: AnySchema): AnySchema {
  let current = schema;
  for (
    let def = getDef(current);
    WRAPPER_TYPES.has(def.type) && def.innerType;
    def = getDef(current)
  ) {
    current = def.innerType;
  }
  return current;
}

/**
 * Adds a labelkey to the given schema.
 */
export function addFieldLabelKey<T>(schema: SchemaPath<T>, labelkey: string) {
  metadata(schema, fieldLabelKeyMetadataKey, () => labelkey);
}

/**
 * Adds a descriptionkey to the given schema.
 */
export function addFieldDescriptionKey<T>(schema: SchemaPath<T>, descriptionkey: string) {
  metadata(schema, fieldDescriptionKeyMetadataKey, () => descriptionkey);
}

function addKeys(path: SchemaPath<unknown>, schema: AnySchema, key: string): void {
  addFieldLabelKey(path, key);
  addFieldDescriptionKey(path, `${key}.description`);

  const def = getDef(unwrap(schema));

  if (def.type === "object" && def.shape) {
    addPropertyKeys(path, def.shape, key);
  } else if (def.type === "array" && def.element) {
    const element = def.element;
    // Items teilen sich den Key des Arrays (kein zusätzliches Segment).
    applyEach(path as SchemaPath<unknown[]>, (item) => {
      addKeys(item as SchemaPath<unknown>, element, key);
    });
  }
}

function addPropertyKeys(
  path: SchemaPath<unknown>,
  shape: Record<string, AnySchema>,
  prefix: string,
): void {
  const children = path as unknown as Record<string, SchemaPath<unknown>>;

  for (const [key, fieldSchema] of Object.entries(shape)) {
    if (key.startsWith("$")) continue; // skip the $type discriminator
    addKeys(children[key], fieldSchema, prefix ? `${prefix}.${key}` : key);
  }
}

/**
 * Adds label keys and description keys to each property of an object schema,
 * recursing through nested objects and arrays in a single pass.
 * Label key: `prefix.property`, description key: `prefix.property.description`.
 */
export function addFieldLabelKeysAndDescriptionKeys<T extends object>(
  path: SchemaPathTree<T>,
  schema: AnySchema,
  prefix = "",
) {
  const def = getDef(unwrap(schema));
  if (def.type !== "object" || !def.shape) {
    throw new Error(
      `addFieldLabelKeysAndDescriptionKeys expects an object schema, got "${def.type}".`,
    );
  }
  addPropertyKeys(path as unknown as SchemaPath<unknown>, def.shape, prefix);
}

/**
 * Names of defined field metadata.
 */
export type FieldMetadataName = "labelKey" | "descriptionKey";

const whatMap = {
  labelKey: fieldLabelKeyMetadataKey,
  descriptionKey: fieldDescriptionKeyMetadataKey,
};

/**
 * Reads metadata from given field.
 * @param field The field to read the metadata from.
 * @param name The name of the metadata to read.
 * @returns Returns the read metadata if present; otherwise undefined.
 */
export function readFieldMetadata<T>(field: Field<T>, name: FieldMetadataName) {
  const state = field();
  const key = whatMap[name];
  return state.hasMetadata(key) ? state.metadata(key)!() : undefined;
}

@Pipe({
  name: "fieldMetadata",
})
/**
 * Pipe to transform data to lookups.
 */
export class FieldMetadataPipe implements PipeTransform {
  transform<T>(value: Field<T> | FieldTree<T>, name: FieldMetadataName) {
    return readFieldMetadata(value, name);
  }
}
