/* eslint-disable @typescript-eslint/naming-convention */
import z from "zod";

import {
  CreateContactPointSchema,
  CreateOrganizationSchema,
  CreatePersonSchema,
} from "./create-item";
import { PreviewContactPointSchema } from "./generated/contact-point";
import { PreviewOrganizationSchema } from "./generated/organization";
import { PreviewOrganizationalUnitSchema } from "./generated/organizational-unit";
import { PreviewPersonSchema } from "./generated/person";
import { mexMeta } from "./zod-mex-meta";

/**
 * Name eines Referenztyps, z. B. "Person".
 * Explizit definiert (nicht aus den Schemas abgeleitet), da er in `GlobalMeta` verwendet wird
 * und sonst eine zirkuläre Typreferenz entsteht.
 */
export type ReferenceType = "Person" | "ContactPoint" | "OrganizationalUnit" | "Organization";

/**
 * Pro Referenztyp die Schemas, die als Wert zulässig sind.
 * `satisfies` stellt sicher, dass genau die Schlüssel von `ReferenceType` vorhanden sind.
 */

const referenceMembers = {
  Person: [CreatePersonSchema, PreviewPersonSchema],
  ContactPoint: [CreateContactPointSchema, PreviewContactPointSchema],
  OrganizationalUnit: [PreviewOrganizationalUnitSchema],
  Organization: [CreateOrganizationSchema, PreviewOrganizationSchema],
} as const satisfies Record<ReferenceType, readonly [z.ZodType, ...z.ZodType[]]>;

type ReferenceMembers = typeof referenceMembers;

/**
 * Schema aller zulässigen Objekte für die Referenztypen `K` (Output- und Input-Typ bleiben erhalten).
 */
export type ReferenceItemSchemaFor<K extends ReferenceType> = z.ZodType<
  z.output<ReferenceMembers[K][number]>,
  z.input<ReferenceMembers[K][number]>
>;

type ReferenceBase = z.ZodString | z.ZodArray<z.ZodString>;

/** Schemas, die `reference()` umlabeln kann (flach definiert, um rekursive Typen zu vermeiden). */
export type ReferenceSource =
  | ReferenceBase
  | z.ZodOptional<ReferenceBase>
  | z.ZodNullable<ReferenceBase>
  | z.ZodOptional<z.ZodNullable<ReferenceBase>>
  | z.ZodNullable<z.ZodOptional<ReferenceBase>>;

/**
 * Type for zod reference result.
 */
export type ReferenceResult<T extends ReferenceSource, K extends ReferenceType> =
  T extends z.ZodOptional<infer Inner extends ReferenceSource>
    ? z.ZodOptional<ReferenceResult<Inner, K>>
    : T extends z.ZodNullable<infer Inner extends ReferenceSource>
      ? z.ZodNullable<ReferenceResult<Inner, K>>
      : T extends z.ZodArray<z.ZodString>
        ? z.ZodArray<ReferenceItemSchemaFor<K>>
        : ReferenceItemSchemaFor<K>;

function buildItemSchema(referenceTypes: readonly ReferenceType[]): z.ZodType {
  const members: z.ZodType[] = referenceTypes.flatMap((type) => [...referenceMembers[type]]);
  const [first, ...rest] = members;
  if (first === undefined) {
    throw new Error("reference() benötigt mindestens einen Referenztyp.");
  }
  return rest.length === 0 ? first : z.union([first, ...rest]);
}

/** Check-Arten, die sich auf die Länge eines Arrays beziehen und daher übertragbar sind. */
const ARRAY_LENGTH_CHECKS: ReadonlySet<string> = new Set([
  "min_length",
  "max_length",
  "length_equals",
]);

/**
 * Überträgt die Längen-Checks (`min`/`max`/`length`/`nonempty`) des Quell-Arrays auf das neue Array.
 * Andere Checks (z. B. `refine`) werden nicht kopiert, da sie sich auf String-Elemente beziehen.
 */
function copyArrayLengthChecks(
  source: z.ZodArray<z.ZodString>,
  target: z.ZodArray<z.ZodType>,
): z.ZodArray<z.ZodType> {
  const checks = (source.def.checks ?? []).filter((check) =>
    ARRAY_LENGTH_CHECKS.has(check._zod.def.check),
  );
  if (checks.length === 0) {
    return target;
  }
  return target.check(...(checks as z.core.$ZodCheck<unknown[]>[]));
}

function buildReference(schema: ReferenceSource, item: z.ZodType): z.ZodType {
  if (schema instanceof z.ZodOptional) {
    return buildReference(schema.unwrap() as ReferenceSource, item).optional();
  }
  if (schema instanceof z.ZodNullable) {
    return buildReference(schema.unwrap() as ReferenceSource, item).nullable();
  }
  if (schema instanceof z.ZodArray) {
    return copyArrayLengthChecks(schema, z.array(item));
  }
  return item;
}

/**
 * Ersetzt ein Referenz-Schema (String bzw. String-Array, ggf. optional/nullable)
 * durch das Schema der Objekte der angegebenen Referenztypen.
 * Optionalität und Nullability bleiben erhalten; Checks des Quellschemas werden nicht übernommen.
 * Die Referenztypen stehen zusätzlich als `referenceTypes` in den Metadaten des Ergebnisschemas
 * (`schema.meta()?.referenceTypes`).
 */
export function reference<T extends ReferenceSource, K extends ReferenceType>(
  schema: T,
  referenceTypes: readonly K[],
): ReferenceResult<T, K> {
  const uniqueTypes = [...new Set(referenceTypes)];
  return mexMeta(buildReference(schema, buildItemSchema(uniqueTypes)), {
    referenceTypes: uniqueTypes,
  }) as ReferenceResult<T, K>;
}
