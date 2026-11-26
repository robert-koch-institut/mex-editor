import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { ValidationError } from "@angular/forms/signals";
import { StandardSchemaValidationError } from "@angular/forms/signals";

import { readFieldMetadata } from "./field-metadata.pipe";

/**
 * Transforms a validation error into a message containing key and param.
 * @param value The error to transform to a message.
 * @returns The transformed error as message.
 */
export function transformValidationErrorToMessage(value: ValidationError.WithFieldTree) {
  if (value instanceof StandardSchemaValidationError) {
    const { message, ...rest } = value.issue;
    return {
      msgKey: message,
      params: {
        ...rest,
        field: `{{${readFieldMetadata(value.fieldTree, "labelKey")}}}`,
      },
    };
  }

  return {
    msgKey: value.message ?? "",
    params: {},
  };
}

@Pipe({
  name: "validationErrorMessage",
})
/**
 * Pipe to transform validation errors into text messages.
 */
export class ValidationErrorMessagePipe implements PipeTransform {
  transform(value: ValidationError.WithFieldTree) {
    return transformValidationErrorToMessage(value);
  }
}
