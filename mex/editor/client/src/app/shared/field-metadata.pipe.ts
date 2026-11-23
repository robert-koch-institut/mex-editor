import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { Field, FieldTree, SchemaPath, SchemaPathTree } from "@angular/forms/signals";
import { createMetadataKey, metadata } from "@angular/forms/signals";

const fieldLabelKeyMetadataKey = createMetadataKey<string>();
const fieldDescriptionKeyMetadataKey = createMetadataKey<string>();

interface ObjectSchemaLike {
  shape: Record<string, unknown>;
}

/**
 * Adds a labelkey to the given schema.
 */
export function addFieldLabelKey<T>(schema: SchemaPath<T>, labelkey: string) {
  metadata(schema, fieldLabelKeyMetadataKey, () => labelkey);
}
/**
 * Adds a labelkey to each property schema for object schema.
 */
export function addFieldLabelKeys<T extends object>(
  path: SchemaPathTree<T>,
  schema: ObjectSchemaLike,
  prefix = "",
) {
  const children = path as unknown as Record<string, SchemaPath<unknown>>;

  for (const [key, fieldSchema] of Object.entries(schema.shape)) {
    if (key.startsWith("$")) continue; // skip the $type discriminator

    const child = children[key];
    const label = prefix ? `${prefix}.${key}` : key;
    console.log("ADDING LABEL for", key, label);

    addFieldLabelKey(child, label);

    if (isObjectSchema(fieldSchema)) {
      addFieldLabelKeys(child as unknown as SchemaPathTree<object>, fieldSchema, label);
    }
  }
}

function isObjectSchema(value: unknown): value is ObjectSchemaLike {
  return typeof value === "object" && value !== null && "shape" in value;
}

/**
 * Adds a descriptionkey to the given schema.
 */
export function addFieldDescriptionKey<T>(schema: SchemaPath<T>, descriptionkey: string) {
  metadata(schema, fieldDescriptionKeyMetadataKey, () => descriptionkey);
}
/**
 * Adds a descriptionkey to each property schema for object schema.
 */
export function addFieldDescriptionKeys<T extends object>(
  path: SchemaPathTree<T>,
  schema: ObjectSchemaLike,
  prefix = "",
) {
  const children = path as unknown as Record<string, SchemaPath<unknown>>;

  for (const [key, fieldSchema] of Object.entries(schema.shape)) {
    if (key.startsWith("$")) continue; // skip the $type discriminator

    const child = children[key];
    const prefixedKey = prefix ? `${prefix}.${key}` : key;
    addFieldDescriptionKey(child, `${prefixedKey}.description`);

    if (isObjectSchema(fieldSchema)) {
      addFieldDescriptionKeys(child as unknown as SchemaPathTree<object>, fieldSchema, prefixedKey);
    }
  }
}

/**
 * Adds a descriptionkey to each property schema for object schema.
 */
export function addFieldLabelKeysAndDescriptionKeys<T extends object>(
  path: SchemaPathTree<T>,
  schema: ObjectSchemaLike,
  prefix = "",
) {
  addFieldLabelKeys(path, schema, prefix);
  addFieldDescriptionKeys(path, schema, prefix);
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
