import type z from "zod";

/**
 * Creates a form model schema by the given schema.
 * Form models exclude optional, since angular forms cant handle undefined and lead to not existing fields.
 * @param schema The schema to create a form model schema from.
 * @returns The created form model schema.
 */
export function formModel<T extends z.ZodObject>(schema: T): z.ZodObject {
  return schema;
}
