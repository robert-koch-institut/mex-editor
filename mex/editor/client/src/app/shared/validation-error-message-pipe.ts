import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { ValidationError } from "@angular/forms/signals";
import { StandardSchemaValidationError } from "@angular/forms/signals";

@Pipe({
  name: "validationErrorMessage",
})
/**
 * Pipe to transform validation errors into text messages.
 */
export class ValidationErrorMessagePipe implements PipeTransform {
  transform(value: ValidationError.WithFieldTree) {
    if (value instanceof StandardSchemaValidationError) {
      const { message, ...rest } = value.issue;
      return {
        msgKey: message,
        params: {
          ...rest,
        },
      };
    }

    return {
      msgKey: value.message,
      params: {},
    };
  }
}
