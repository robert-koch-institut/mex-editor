import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { Field, FieldTree, SchemaPath, SchemaPathTree } from "@angular/forms/signals";
import { createMetadataKey, metadata } from "@angular/forms/signals";

/** SignalForm metadata key for field labelkey. */
export const fieldLabelKeyMetadataKey = createMetadataKey<string>();
/** SignalForm metadata key for field description. */
export const fieldDescriptionKeyMetadataKey = createMetadataKey<string>();

/**
 * Adds a labelkey to the given schema.
 */
export function addFieldLabelKey<T>(schema: SchemaPath<T>, labelkey: string) {
  metadata(schema, fieldLabelKeyMetadataKey, () => labelkey);
}
/**
 * Adds a labelkey to each property schema for object schema.
 */
export function addFieldLabelKeys<T extends object>(path: SchemaPathTree<T>, prefix = "") {
  const children = path as unknown as Record<string, SchemaPath<unknown>>;

  for (const key of Object.keys(children)) {
    if (key.startsWith("$")) continue;
    const labelkey = prefix ? `${prefix}.${key}` : key;
    addFieldLabelKey(children[key], labelkey);
  }
}

/**
 * Adds a descriptionkey to the given schema.
 */
export function addFieldDescriptionKey<T>(schema: SchemaPath<T>, descriptionkey: string) {
  metadata(schema, fieldLabelKeyMetadataKey, () => descriptionkey);
}
/**
 * Adds a descriptionkey to each property schema for object schema.
 */
export function addFieldDescriptionKeys<T extends object>(path: SchemaPathTree<T>, prefix = "") {
  const children = path as unknown as Record<string, SchemaPath<unknown>>;

  for (const key of Object.keys(children)) {
    if (key.startsWith("$")) continue;
    const descriptionkeyKey = `${key}.descriptionkey`;
    const descriptionkey = prefix ? `${prefix}.${descriptionkeyKey}` : descriptionkeyKey;
    addFieldDescriptionKey(children[key], descriptionkey);
  }
}

/**
 * Adds a descriptionkey to each property schema for object schema.
 */
export function addFieldLabelKeysAndDescriptionKeys<T extends object>(
  path: SchemaPathTree<T>,
  prefix = "",
) {
  addFieldLabelKeys(path, prefix);
  addFieldDescriptionKeys(path, prefix);
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
export function readFieldMetadata<T>(field: Field<T> | FieldTree<T>, name: FieldMetadataName) {
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
