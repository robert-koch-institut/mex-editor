import type { PipeTransform } from "@angular/core";
import { Pipe } from "@angular/core";

import type { SubmissionFailure } from "./models/submission-result";

@Pipe({
  name: "errorMailTo",
})
/**
 * A pipe that generates a mailto link for errors.
 */
export class ErrorMailToPipe implements PipeTransform {
  buildErrorSummary(error: SubmissionFailure<unknown>) {
    return {
      subject: "Fehler beim Speichern einer Resource.",
      content:
        `Fehler beim Speichern einer Resource!\n` +
        `--- PAYLOAD ---\n` +
        `${JSON.stringify(error.payload, null, 2)}\n\n` +
        `--- ERROR DETAILS ---\n` +
        `${JSON.stringify(error.error, null, 2)} `,
    };
  }

  transform(failure: SubmissionFailure<unknown>): string {
    const summary = this.buildErrorSummary(failure);
    const body =
      `Hallo MeX-Support,\n\n` +
      `leider ist ein Fehler im Editor aufgetreten.\n\n` +
      `${summary.content}`;

    // Sicheres URL-Encoding für Sonderzeichen und Zeilenumbrüche
    return `mailto:Mex@rki.de?subject=${encodeURIComponent(summary.subject)}&body=${encodeURIComponent(body)}`;
  }
}
