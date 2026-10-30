import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

import type { SubmissionError } from "./models/submission-result";

@Pipe({
  name: "errorMailTo",
})
/**
 * A pipe that generates a mailto link for errors.
 */
export class ErrorMailToPipe<T extends { $type: string }> implements PipeTransform {
  buildErrorSummary(error: SubmissionError<T>) {
    const title = `Fehler beim Speichern von '${error.payload.$type}'`;
    const inner = error.innerError
      ? {
          ...error.innerError,
          name: error.innerError.name,
          message: error.innerError.message,
        }
      : {};
    return {
      subject: title,
      content:
        `${title}!\n` +
        `--- PAYLOAD ---\n` +
        `${JSON.stringify(error.payload, null, 2)}\n\n` +
        `--- ERROR DETAILS ---\n` +
        `${JSON.stringify(inner, null, 2)} `,
    };
  }

  transform(error: SubmissionError<T>): string {
    const summary = this.buildErrorSummary(error);
    const body =
      `Hallo MEx-Support,\n\n` +
      `leider ist ein Fehler im Editor aufgetreten.\n\n` +
      `${summary.content}`;

    // Sicheres URL-Encoding für Sonderzeichen und Zeilenumbrüche
    return `mailto:mex@rki.de?subject=${encodeURIComponent(summary.subject)}&body=${encodeURIComponent(body)}`;
  }
}
