import { HttpErrorResponse } from "@angular/common/http";
import { HttpTestingController, type TestRequest } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";
import { vi } from "vitest";

import type { FastTrackResourceModel } from "./fast-track-resource.models";
import { FastTrackResourceSubmission } from "./fast-track-resource-submission";

/*
 * Notes / assumptions:
 *
 * 1. HttpClient + the testing backend come from the project's global test
 *    providers, the real TranslocoService too (only `getActiveLang` is
 *    spied where a test needs a specific language).
 * 2. Model fixtures are cast through `unknown`: the real
 *    FastTrackResourceModel is zod-inferred (enum-typed theme/frequency,
 *    PreviewPerson/... items), and this service only reads `identifier`
 *    and `$type` from reference items -- no need to build fully
 *    schema-valid objects here.
 * 3. `isCreateItem` (shared/models/create-item) wasn't available to me;
 *    fixtures use `$type: "CreatePerson" | "CreateContactPoint"`, which
 *    is what `submitCreateItem` itself branches on.
 * 4. All sub-submissions and the final resource go to the same URL
 *    (`api/v0/backend/rule-set`), so requests are told apart by body:
 *    `entityType` for the sub-submissions, `$type` for the resource.
 */

const RULE_SET_URL = "api/v0/backend/rule-set";

type Body = Record<string, unknown>;
type ModelOverrides = { [K in keyof FastTrackResourceModel]?: unknown };

const makeModel = (overrides: ModelOverrides = {}): FastTrackResourceModel =>
  ({
    title: "Titel",
    description: "Beschreibung",
    theme: [],
    resourceTypeGeneral: [],
    spatial: "Berlin",
    resourceCreationMethod: ["method-1"],
    accrualPeriodicity: "freq-1",
    start: null,
    end: null,
    hasLegalBasis: "Rechtsgrundlage",
    provenance: "Herkunft",
    rights: "Rechte",
    keywords: { de: ["Gesundheit"], en: ["health"] },
    unitInCharge: [],
    contact: [],
    creator: [],
    contributingUnit: [],
    contributor: [],
    ...overrides,
  }) as unknown as FastTrackResourceModel;

const previewPerson = (identifier: string) => ({
  $type: "PreviewPerson",
  identifier,
  fullName: [{ value: identifier }],
});
const previewUnit = (identifier: string) => ({
  $type: "PreviewOrganizationalUnit",
  identifier,
  shortName: [{ value: identifier }],
});
const createPerson = (givenName = "Jane", familyName = "Doe") => ({
  $type: "CreatePerson",
  givenName,
  familyName,
});
const createContactPoint = (email = "info@example.org") => ({
  $type: "CreateContactPoint",
  email,
});

/** Wraps a promise so a rejection is observed immediately (no unhandled-rejection noise). */
function track<T>(promise: Promise<T>) {
  const state: { status: "pending" | "resolved" | "rejected"; value?: T; error?: unknown } = {
    status: "pending",
  };
  const done = promise.then(
    (value) => {
      state.status = "resolved";
      state.value = value;
    },
    (error: unknown) => {
      state.status = "rejected";
      state.error = error;
    },
  );
  return { state, done };
}

// eslint-disable-next-line max-lines-per-function
describe("FastTrackResourceSubmission", () => {
  let service: FastTrackResourceSubmission;
  let http: HttpTestingController;

  const bodyOf = (req: TestRequest) => req.request.body as Body;
  const subRequests = (entityType: "PersonRuleSetRequest" | "ContactPointRuleSetRequest") =>
    http.match((r) => r.url === RULE_SET_URL && (r.body as Body)?.["entityType"] === entityType);
  const resourceRequests = () =>
    http.match(
      (r) => r.url === RULE_SET_URL && (r.body as Body)?.["$type"] === "ResourceRuleSetRequest",
    );

  beforeEach(() => {
    service = TestBed.inject(FastTrackResourceSubmission);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // cancelled requests (aborted because a sibling failed) are expected in some tests
    http.verify({ ignoreCancelled: true });
    vi.restoreAllMocks();
  });

  describe("mapModel", () => {
    const emptyRefs = {
      contact: [],
      contributor: [],
      unitInCharge: [],
      creator: [],
      contributingUnit: [],
    };

    it("wraps single-language text fields as { value, language } using the given language", () => {
      const additive = service.mapModel(makeModel(), emptyRefs, "en");

      expect(additive["$type"]).toBe("AdditiveResource");
      expect(additive["title"]).toEqual([{ value: "Titel", language: "en" }]);
      expect(additive["description"]).toEqual([{ value: "Beschreibung", language: "en" }]);
      expect(additive["provenance"]).toEqual([{ value: "Herkunft", language: "en" }]);
      expect(additive["rights"]).toEqual([{ value: "Rechte", language: "en" }]);
      expect(additive["spatial"]).toEqual([{ value: "Berlin", language: "en" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "Rechtsgrundlage", language: "en" }]);
    });

    it("tags keywords with their OWN language, regardless of the language argument", () => {
      const additive = service.mapModel(makeModel(), emptyRefs, "en");

      expect(additive["keyword"]).toEqual([
        { value: "Gesundheit", language: "de" },
        { value: "health", language: "en" },
      ]);
    });

    it("emits German keywords before English ones, each list in its original order", () => {
      const model = makeModel({ keywords: { de: ["a", "b"], en: ["x", "y"] } });
      const additive = service.mapModel(model, emptyRefs, "de");

      expect((additive["keyword"] as { value: string }[]).map((k) => k.value)).toEqual([
        "a",
        "b",
        "x",
        "y",
      ]);
    });

    it("passes the resolved reference ids through untouched", () => {
      const refs = {
        contact: ["c1"],
        contributor: ["p1", "p2"],
        unitInCharge: ["u1"],
        creator: ["p3"],
        contributingUnit: ["u2"],
      };
      const additive = service.mapModel(makeModel(), refs, "de");

      expect(additive["contact"]).toEqual(["c1"]);
      expect(additive["contributor"]).toEqual(["p1", "p2"]);
      expect(additive["unitInCharge"]).toEqual(["u1"]);
      expect(additive["creator"]).toEqual(["p3"]);
      expect(additive["contributingUnit"]).toEqual(["u2"]);
    });

    it("passes vocabulary values through as-is", () => {
      const model = makeModel({
        theme: ["theme-1"],
        resourceTypeGeneral: ["type-1"],
        resourceCreationMethod: ["method-1"],
        accrualPeriodicity: "freq-1",
      });
      const additive = service.mapModel(model, emptyRefs, "de");

      expect(additive["theme"]).toEqual(["theme-1"]);
      expect(additive["resourceTypeGeneral"]).toEqual(["type-1"]);
      expect(additive["resourceCreationMethod"]).toEqual(["method-1"]);
      expect(additive["accrualPeriodicity"]).toBe("freq-1");
    });

    it("formats start/end as ISO dates (date only, no time)", () => {
      const model = makeModel({
        start: DateTime.fromISO("2026-01-05T23:30:00"),
        end: DateTime.fromISO("2026-12-31T00:00:00"),
      });
      const additive = service.mapModel(model, emptyRefs, "de");

      expect(additive["start"]).toEqual(["2026-01-05"]);
      expect(additive["end"]).toEqual(["2026-12-31"]);
    });

    it("leaves start/end undefined when they are not set", () => {
      const additive = service.mapModel(makeModel({ start: null, end: null }), emptyRefs, "de");

      expect(additive["start"]).toBeUndefined();
      expect(additive["end"]).toBeUndefined();
    });
  });

  describe("submit: resource without any new reference items", () => {
    it("sends exactly one request, with the preview items' identifiers, and resolves with the response", async () => {
      const model = makeModel({
        contact: [previewPerson("contact-1")],
        contributor: [previewPerson("person-1"), previewPerson("person-2")],
        unitInCharge: [previewUnit("unit-1")],
        creator: [previewPerson("person-3")],
        contributingUnit: [previewUnit("unit-2")],
      });

      const { state, done } = track(service.submit(model));

      expect(subRequests("PersonRuleSetRequest")).toHaveLength(0);
      expect(subRequests("ContactPointRuleSetRequest")).toHaveLength(0);
      const [request] = resourceRequests();
      expect(request.request.method).toBe("POST");
      const additive = (bodyOf(request)["additive"] ?? {}) as Body;
      expect(bodyOf(request)["$type"]).toBe("ResourceRuleSetRequest");
      expect(additive["contact"]).toEqual(["contact-1"]);
      expect(additive["contributor"]).toEqual(["person-1", "person-2"]);
      expect(additive["unitInCharge"]).toEqual(["unit-1"]);
      expect(additive["creator"]).toEqual(["person-3"]);
      expect(additive["contributingUnit"]).toEqual(["unit-2"]);

      const response = { $type: "ResourceRuleSetResponse", stableTargetId: "res-1" };
      request.flush(response);
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toEqual({ success: true, response });
    });

    it("works with all reference lists empty", async () => {
      const { state, done } = track(service.submit(makeModel()));

      const [request] = resourceRequests();
      const additive = (bodyOf(request)["additive"] ?? {}) as Body;
      expect(additive["contact"]).toEqual([]);
      expect(additive["creator"]).toEqual([]);

      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;

      expect(state.value).toMatchObject({ success: true });
    });
  });

  // eslint-disable-next-line max-lines-per-function
  describe("submit: creating new reference items first", () => {
    it("posts a new Person as a PersonRuleSetRequest and uses the returned stableTargetId", async () => {
      const { state, done } = track(
        service.submit(makeModel({ creator: [createPerson("Jane", "Doe")] })),
      );

      const [personRequest] = subRequests("PersonRuleSetRequest");
      expect(personRequest.request.method).toBe("POST");
      expect(bodyOf(personRequest)).toEqual({
        additive: { givenName: ["Jane"], familyName: ["Doe"], entityType: "AdditivePerson" },
        entityType: "PersonRuleSetRequest",
      });
      personRequest.flush({ stableTargetId: "newPerson0001" });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["creator"]).toEqual([
        "newPerson0001",
      ]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;

      expect(state.value).toMatchObject({ success: true });
    });

    it("posts a new ContactPoint as a ContactPointRuleSetRequest and uses the returned stableTargetId", async () => {
      const { done } = track(
        service.submit(makeModel({ contact: [createContactPoint("info@example.org")] })),
      );

      const [contactRequest] = subRequests("ContactPointRuleSetRequest");
      expect(bodyOf(contactRequest)).toEqual({
        additive: { email: "info@example.org", entityType: "AdditiveContactPoint" },
        entityType: "ContactPointRuleSetRequest",
      });
      contactRequest.flush({ stableTargetId: "newContact001" });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["contact"]).toEqual([
        "newContact001",
      ]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("does not send the resource until EVERY sub-submission has been answered", async () => {
      const model = makeModel({ contact: [createContactPoint()], creator: [createPerson()] });
      const { done } = track(service.submit(model));

      const [personRequest] = subRequests("PersonRuleSetRequest");
      const [contactRequest] = subRequests("ContactPointRuleSetRequest");

      personRequest.flush({ stableTargetId: "person00000001" });
      expect(resourceRequests()).toHaveLength(0); // contact still outstanding
      expect(contactRequest.cancelled).toBe(false); // control: a pending sibling is NOT aborted normally

      contactRequest.flush({ stableTargetId: "contact0000001" });
      const [resourceRequest] = resourceRequests();
      expect(resourceRequest).toBeDefined();

      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("keeps the original list order in the result, no matter in which order the answers arrive", async () => {
      const model = makeModel({
        contributor: [
          previewPerson("existing-1"),
          createPerson("A", "One"),
          createPerson("B", "Two"),
        ],
      });
      const { done } = track(service.submit(model));

      const [first, second] = subRequests("PersonRuleSetRequest");
      expect(bodyOf(first)["additive"]).toMatchObject({ givenName: ["A"] });
      // answer the SECOND one first
      second.flush({ stableTargetId: "id-for-B" });
      first.flush({ stableTargetId: "id-for-A" });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["contributor"]).toEqual([
        "existing-1",
        "id-for-A",
        "id-for-B",
      ]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("creates items for several lists independently and puts each id into the right list", async () => {
      const model = makeModel({
        contact: [createContactPoint("c@example.org")],
        creator: [createPerson("C", "Creator")],
        contributor: [createPerson("D", "Contributor")],
      });
      const { state, done } = track(service.submit(model));

      const [contactRequest] = subRequests("ContactPointRuleSetRequest");
      const personRequests = subRequests("PersonRuleSetRequest");
      expect(personRequests).toHaveLength(2);
      const givenNameOf = (r: TestRequest) =>
        ((bodyOf(r)["additive"] as Body)["givenName"] as string[])[0];
      personRequests
        .find((r) => givenNameOf(r) === "C")!
        .flush({ stableTargetId: "creator000001" });
      personRequests
        .find((r) => givenNameOf(r) === "D")!
        .flush({ stableTargetId: "contrib000001" });
      expect(resourceRequests()).toHaveLength(0); // the contact is still outstanding
      contactRequest.flush({ stableTargetId: "contact000001" });

      const [resourceRequest] = resourceRequests();
      const additive = (bodyOf(resourceRequest)["additive"] ?? {}) as Body;
      expect(additive["creator"]).toEqual(["creator000001"]);
      expect(additive["contributor"]).toEqual(["contrib000001"]);
      expect(additive["contact"]).toEqual(["contact000001"]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;

      expect(state.value).toMatchObject({ success: true });
    });
  });

  describe("submit: the resource request itself fails", () => {
    it("resolves (does not reject) with success:false, the payload that was sent, and the error", async () => {
      const { state, done } = track(
        service.submit(makeModel({ contact: [previewPerson("contact-1")] })),
      );

      const [request] = resourceRequests();
      request.flush("Internal Server Error", { status: 500, statusText: "Server Error" });
      await done;

      expect(state.status).toBe("resolved");
      const result = state.value as unknown as {
        success: boolean;
        payload: Body;
        error: HttpErrorResponse;
      };
      expect(result.success).toBe(false);
      expect(result.payload["$type"]).toBe("ResourceRuleSetRequest");
      expect(result.payload).toEqual(bodyOf(request));
      expect(result.error).toBeInstanceOf(HttpErrorResponse);
      expect(result.error).toMatchObject({ status: 500 });
    });

    it("reports a network error (status 0) the same way", async () => {
      const { state, done } = track(service.submit(makeModel()));

      const [request] = resourceRequests();
      request.error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toMatchObject({ success: false, error: { status: 0 } });
    });

    it("still contains the ids of items that were already created before the failure", async () => {
      const { state, done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      subRequests("PersonRuleSetRequest")[0].flush({ stableTargetId: "person00000001" });
      const [request] = resourceRequests();
      request.flush("nope", { status: 422, statusText: "Unprocessable Entity" });
      await done;

      const payload = (state.value as unknown as { payload: { additive: Body } }).payload;
      expect(payload.additive["creator"]).toEqual(["person00000001"]);
    });
  });

  describe("submit: a sub-submission fails", () => {
    // NOTE: unlike a failing resource request (which resolves with success:false), a failing
    // sub-submission makes submit() REJECT -- the payload doesn't exist yet at that point, so
    // there's nothing to put into a SubmissionFailure. Callers must handle both shapes.

    it.each([
      ["contact", { contact: [createContactPoint()] }],
      ["creator", { creator: [createPerson()] }],
      ["contributor", { contributor: [createPerson()] }],
    ] as [string, ModelOverrides][])(
      "rejects with the HTTP error when creating a new item in '%s' fails",
      async (_list, overrides) => {
        const { state, done } = track(service.submit(makeModel(overrides)));

        const [request] = [
          ...subRequests("PersonRuleSetRequest"),
          ...subRequests("ContactPointRuleSetRequest"),
        ];
        request.flush("Internal Server Error", { status: 500, statusText: "Server Error" });
        await done;

        expect(state.status).toBe("rejected");
        expect(state.error).toBeInstanceOf(HttpErrorResponse);
        expect(state.error).toMatchObject({ status: 500 });
      },
    );

    it("never sends the resource when a sub-submission failed", async () => {
      const { done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      subRequests("PersonRuleSetRequest")[0].flush("fail", {
        status: 500,
        statusText: "Server Error",
      });
      await done;

      expect(resourceRequests()).toHaveLength(0);
    });

    it("rejects with a network error (status 0) as well", async () => {
      const { state, done } = track(service.submit(makeModel({ contact: [createContactPoint()] })));

      subRequests("ContactPointRuleSetRequest")[0].error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("rejected");
      expect(state.error).toMatchObject({ status: 0 });
    });

    it("cancels the sub-submissions that are still in flight when one of them fails", async () => {
      const model = makeModel({
        contact: [createContactPoint()],
        creator: [createPerson("A", "One")],
        contributor: [createPerson("B", "Two")],
      });
      const { state, done } = track(service.submit(model));

      const personRequests = subRequests("PersonRuleSetRequest");
      const [contactRequest] = subRequests("ContactPointRuleSetRequest");
      expect(personRequests).toHaveLength(2);

      contactRequest.flush("fail", { status: 500, statusText: "Server Error" });
      await done;

      expect(state.status).toBe("rejected");
      expect(personRequests[0].cancelled).toBe(true);
      expect(personRequests[1].cancelled).toBe(true);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("rejects when a failure comes AFTER another sub-submission already succeeded (that item stays created, no rollback)", async () => {
      const model = makeModel({
        creator: [createPerson("A", "One")],
        contact: [createContactPoint()],
      });
      const { state, done } = track(service.submit(model));

      const [personRequest] = subRequests("PersonRuleSetRequest");
      const [contactRequest] = subRequests("ContactPointRuleSetRequest");

      personRequest.flush({ stableTargetId: "person00000001" }); // already persisted on the backend
      contactRequest.flush("fail", { status: 503, statusText: "Service Unavailable" });
      await done;

      expect(state.status).toBe("rejected");
      expect(state.error).toMatchObject({ status: 503 });
      expect(resourceRequests()).toHaveLength(0);
      // no compensating request (e.g. a delete) is sent for the person that was already created
      http.expectNone((r) => r.method !== "POST");
    });

    it("rejects only once even if several sub-submissions fail", async () => {
      const model = makeModel({ creator: [createPerson("A", "One"), createPerson("B", "Two")] });
      const { state, done } = track(service.submit(model));

      const [first, second] = subRequests("PersonRuleSetRequest");
      first.flush("fail", { status: 500, statusText: "Server Error" });
      await done;

      expect(second.cancelled).toBe(true); // second never gets a chance to fail separately
      expect(state.error).toMatchObject({ status: 500 });
    });

    it("stays usable after a failed submit (no state carried over)", async () => {
      const failing = track(service.submit(makeModel({ creator: [createPerson()] })));
      subRequests("PersonRuleSetRequest")[0].flush("fail", {
        status: 500,
        statusText: "Server Error",
      });
      await failing.done;
      expect(failing.state.status).toBe("rejected");

      const retry = track(service.submit(makeModel({ creator: [createPerson()] })));
      subRequests("PersonRuleSetRequest")[0].flush({ stableTargetId: "person00000002" });
      resourceRequests()[0].flush({ $type: "ResourceRuleSetResponse" });
      await retry.done;

      expect(retry.state.status).toBe("resolved");
      expect(retry.state.value).toMatchObject({ success: true });
    });
  });

  describe("language", () => {
    const languageOfTitle = (request: TestRequest) =>
      (((bodyOf(request)["additive"] ?? {}) as Body)["title"] as { language: string }[])[0]
        .language;

    it("uses German texts when the active language is 'de'", async () => {
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("de");
      const { done } = track(service.submit(makeModel()));

      const [request] = resourceRequests();
      expect(languageOfTitle(request)).toBe("de");
      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("falls back to German for a language that is neither 'de' nor 'en'", async () => {
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("fr");
      const { done } = track(service.submit(makeModel()));

      const [request] = resourceRequests();
      expect(languageOfTitle(request)).toBe("de");
      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    // KNOWN BUG: `isValidLanguage` does `value in ["en", "de"]`. The `in` operator checks an
    // array's *keys* ("0", "1", "length", ...), not its values, so "en" is never recognised and
    // every submission is sent as German. Fix: `["en", "de"].includes(value)`. Once fixed, this
    // test starts passing and `it.fails` flips it to a failure -- remove `.fails` then.
    it.fails("uses English texts when the active language is 'en'", async () => {
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("en");
      const { done } = track(service.submit(makeModel()));

      const [request] = resourceRequests();
      expect(languageOfTitle(request)).toBe("en");
      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });
  });
});
