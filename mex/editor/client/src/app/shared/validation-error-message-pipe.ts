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
      const isNestedIssue = value.issue.path && value.issue.path.length >= 2;
      if (isNestedIssue) {
        const indexer = value.issue.path[1];
        if (typeof indexer === "number") {
          return {
            msgKey: "validation.arrayError",
            params: {
              index: indexer + 1,
            },
          };
        }
        return {
          msgKey: "validation.objectError",
          params: {
            index: indexer,
          },
        };
      }

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
