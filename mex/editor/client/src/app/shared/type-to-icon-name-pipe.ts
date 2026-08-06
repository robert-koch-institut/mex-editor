import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

/**
 * Options for the TypeToIconNamePipe transform.
 */
export interface TypeToIconNameOptions {
  prefix?: string;
  suffix?: string;
  fallback?: string;
}

@Pipe({
  name: "typeToIconName",
})
/**
 * Pipe to transform a type to icon name.
 *
 * The type is normalized by the following rules:
 * 1. Remove prefix "Merged|Extracted|Preview"
 */
export class TypeToIconNamePipe implements PipeTransform {
  private readonly _unknownTypeName = "question_mark";
  private readonly _typeToNameMap = new Map<string, string>([
    ["Person", "person"],
    ["Resource", "database"],
    ["ContactPoint", "mail"],
    ["Organization", "domain"],
    ["OrganizationalUnit", "ad_group"],
  ]);

  private _prefixTrim = /^Merged|Extracted|Preview|Create/;
  private _normalizeType(type: string): string {
    return type.replace(this._prefixTrim, "");
  }

  transform(value: string, options: TypeToIconNameOptions = {}): string {
    const normalizedType = this._normalizeType(value);
    const mapped = this._typeToNameMap.get(normalizedType);
    if (mapped) {
      return `${options.prefix ?? ""}${mapped}${options.suffix ?? ""}`;
    }
    return options.fallback ?? this._unknownTypeName;
  }
}
