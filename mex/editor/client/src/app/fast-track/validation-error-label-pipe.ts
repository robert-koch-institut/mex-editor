import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";
import type { FieldState, ValidationError } from "@angular/forms/signals";
import { StandardSchemaValidationError } from "@angular/forms/signals";

import { LabeledControl } from "./labeled-control";

@Pipe({
  name: "validationErrorMessage",
})
/**
 * Pipe to transform validation errors into text messages.
 */
export class ValidationErrorMessagePipe implements PipeTransform {
  private relativePath(error: ValidationError.WithFieldTree, state: FieldState<unknown>): string[] {
    if (
      error instanceof StandardSchemaValidationError &&
      error.issue.path &&
      error.issue.path.length >= 1
    ) {
      const [_, ...others] = error.issue.path;
      return others.map((x) => x.toString());
    }

    const prefix = `${state.name()}.`;
    const errorName = error.fieldTree().name();
    return errorName.startsWith(prefix) ? errorName.slice(prefix.length).split(".") : [];
  }

  transform(value: ValidationError.WithFieldTree, state: FieldState<unknown>) {
    const formPath = this.relativePath(value, state);
    if (formPath.length > 0) {
      const [indexer, ..._others] = formPath;
      const arrayIndexer = Number(indexer);
      if (Number.isNaN(arrayIndexer)) {
        const binding = state.formFieldBindings().find((x) => x.state().name() === state.name());
        if (binding) {
          const component = binding.injector.get(LabeledControl, null);
          return {
            msgKey: "validation.objectError",
            params: {
              index: component?.labels[indexer](),
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
      return {
        msgKey: "validation.arrayError",
        params: {
          index: arrayIndexer + 1,
        },
      };
    }
    if (value instanceof StandardSchemaValidationError) {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { message, ...rest } = value.issue;
      return {
        msgKey: value.message,
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
