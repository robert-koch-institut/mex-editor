import { HttpErrorResponse } from "@angular/common/http";

import { SubmissionError } from "../fast-track/fast-track-resource/fast-track-resource-submission";
import { ErrorMailToPipe } from "./error-mail-to-pipe";

const makeFailure = <T extends { $type: string }>(
  payload: T = {
    $type: "ResourceRuleSetRequest",
    additive: { title: [{ value: "Titel" }] },
  } as unknown as T,
  error: Error = new HttpErrorResponse({ status: 500, statusText: "Server Error", url: "api/x" }),
) => new SubmissionError(payload, error);

/** Splits the generated mailto link into its decoded parts. */
function parse(link: string) {
  const url = new URL(link);
  return {
    protocol: url.protocol,
    recipient: decodeURIComponent(url.pathname),
    subject: url.searchParams.get("subject"),
    body: url.searchParams.get("body"),
  };
}

// eslint-disable-next-line max-lines-per-function
describe("ErrorMailToPipe", () => {
  let pipe: ErrorMailToPipe<{ $type: string }>;

  beforeEach(() => {
    pipe = new ErrorMailToPipe();
  });

  describe("transform", () => {
    it("builds a mailto link to the MEx support address", () => {
      const { protocol, recipient } = parse(pipe.transform(makeFailure()));

      expect(protocol).toBe("mailto:");
      expect(recipient).toBe("mex@rki.de");
    });

    it("sets the subject", () => {
      expect(parse(pipe.transform(makeFailure())).subject).not.toBe("");
    });

    it("greets the support team at the start of the body", () => {
      const { body } = parse(pipe.transform(makeFailure()));

      expect(body).toMatch(
        /^Hallo MEx-Support,\n\nleider ist ein Fehler im Editor aufgetreten\.\n\n/,
      );
    });

    it("contains the payload as pretty-printed JSON", () => {
      const payload = {
        $type: "ResourceRuleSetRequest",
        additive: { title: [{ value: "Titel" }] },
      };
      const { body } = parse(pipe.transform(makeFailure(payload)));

      expect(body).toContain("--- PAYLOAD ---\n" + JSON.stringify(payload, null, 2));
    });

    it("contains the error details after the payload", () => {
      const { body } = parse(pipe.transform(makeFailure()));

      expect(body).toContain("--- ERROR DETAILS ---\n");
      expect(body!.indexOf("--- PAYLOAD ---")).toBeLessThan(body!.indexOf("--- ERROR DETAILS ---"));
    });

    it("includes status and message of an HttpErrorResponse in the error details", () => {
      const error = new HttpErrorResponse({
        status: 503,
        statusText: "Service Unavailable",
        url: "api/v0/backend/rule-set",
      });
      const { body } = parse(pipe.transform(makeFailure({ $type: "Type" }, error)));
      const details = body!.split("--- ERROR DETAILS ---\n")[1];

      expect(JSON.parse(details)).toMatchObject({ status: 503, statusText: "Service Unavailable" });
      expect(details).toContain("api/v0/backend/rule-set");
    });

    it("includes the server's error body from an HttpErrorResponse", () => {
      const error = new HttpErrorResponse({
        status: 422,
        error: { detail: "title must not be empty" },
      });
      const { body } = parse(pipe.transform(makeFailure({ $type: "payload" }, error)));

      expect(body).toContain("title must not be empty");
    });

    it("is stable: the same failure always produces the same link", () => {
      const failure = makeFailure();

      expect(pipe.transform(failure)).toBe(pipe.transform(failure));
    });
  });

  describe("encoding", () => {
    const nasty = 'Ärger & Öl = "ü" #1? 100% <b>fett</b> 😀\nzweite Zeile\ttab';

    it("round-trips umlauts, quotes, emoji, newlines and tabs through the link unchanged", () => {
      const { body } = parse(pipe.transform(makeFailure({ $type: "payload", text: nasty })));
      const payloadJson = body!.split("--- PAYLOAD ---\n")[1].split("\n\n--- ERROR DETAILS ---")[0];

      expect(JSON.parse(payloadJson)).toEqual({ $type: "payload", text: nasty });
    });

    it("never leaves raw whitespace, '#' or a stray '&' in the link (they would break the mailto URL)", () => {
      const link = pipe.transform(makeFailure({ $type: "payload", text: nasty }));

      expect(link).not.toMatch(/\s/);
      expect(link).not.toContain("#");
      // exactly one '&': the separator between subject and body
      expect(link.split("&")).toHaveLength(2);
      expect(link.split("?")).toHaveLength(2);
    });

    it("keeps '+' in the payload a '+' (not turned into a space)", () => {
      const { body } = parse(
        pipe.transform(makeFailure({ $type: "payload", phone: "+49 30 1234" })),
      );

      expect(body).toContain("+49 30 1234");
    });
  });

  describe("buildErrorSummary", () => {
    it("returns the subject and the payload/error content block", () => {
      const summary = pipe.buildErrorSummary(makeFailure({ $type: "PayloadType", a: 1 }));

      expect(summary.subject).toBe("Fehler beim Speichern von 'PayloadType'");
      expect(summary.content).toContain("--- PAYLOAD ---");
      expect(summary.content).toContain('"a": 1');
      expect(summary.content).toContain("--- ERROR DETAILS ---");
    });
  });

  describe("limitations", () => {
    // KNOWN LIMITATION: JSON.stringify(new Error("boom")) is "{}" -- name/message/stack are not
    // enumerable, so a plain Error loses its message in the mail. HttpErrorResponse (the normal
    // case here) is fine, see above. A fix could serialize `{ name, message, ...error }`.
    // Once fixed this starts passing and `it.fails` flips it to a failure -- remove `.fails` then.
    it.fails("includes the message of a plain Error in the error details", () => {
      const { body } = parse(
        pipe.transform(makeFailure({ $type: "payload" }, new Error("Das ist die Fehlermeldung"))),
      );

      expect(body).toContain("Das ist die Fehlermeldung");
    });

    // A resource payload easily gets big; many mail clients/browsers truncate mailto links
    // somewhere around 2000 characters. This just records how fast that limit is reached.
    it("produces a link well beyond 2000 characters for a realistic payload", () => {
      const keyword = (i: number) => ({ value: `Schlagwort ${i}`, language: "de" });
      const payload = {
        $type: "",
        additive: { keyword: Array.from({ length: 40 }, (_, i) => keyword(i)) },
      };

      expect(pipe.transform(makeFailure(payload)).length).toBeGreaterThan(2000);
    });
  });
});
