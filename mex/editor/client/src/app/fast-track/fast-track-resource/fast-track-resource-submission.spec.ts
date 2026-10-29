import { HttpErrorResponse } from "@angular/common/http";
import { HttpTestingController, type TestRequest } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { TranslocoService } from "@jsverse/transloco";
import { DateTime } from "luxon";
import { vi } from "vitest";

import type { FastTrackResourceModel } from "./fast-track-resource.models";
import { FastTrackResourceSubmission, SubmissionError } from "./fast-track-resource-submission";

/*
 * Notes:
 *
 * 1. HttpClient + the testing backend come from the project's global test providers
 *    (src/test-providers.ts). The language is pinned per test via `mockActiveLang`, so the tests
 *    don't depend on the default test language.
 * 2. The service validates everything with the real Zod schemas, so fixtures must be valid:
 *    reference ids match the identifier pattern (14-22 letters/digits, see `id()`), vocabulary
 *    values are real enum members, and texts must not be empty.
 * 3. Model fixtures are cast through `unknown`: the service only reads `identifier` and `$type`
 *    of reference items, so they don't need to be complete Preview* objects.
 * 4. The resource and the new Person/ContactPoint items all go to the same URL
 *    (`api/v0/backend/rule-set`), so requests are told apart by the `$type` of their body.
 * 5. `submit()` is supposed to never reject: every error ends up as `{ success: false, error }`.
 *    Errors of a request are a `SubmissionError` (`payload` = the request that failed,
 *    `innerError` = why). The two `it.fails` tests below are known gaps in that promise.
 */

const RULE_SET_URL = "api/v0/backend/rule-set";

const THEME = "https://mex.rki.de/item/theme-1";
const RESOURCE_TYPE_GENERAL = "https://mex.rki.de/item/resource-type-general-2";
const RESOURCE_CREATION_METHOD = "https://mex.rki.de/item/resource-creation-method-1";
const FREQUENCY = "https://mex.rki.de/item/frequency-1";

type Body = Record<string, unknown>;
type ModelOverrides = { [K in keyof FastTrackResourceModel]?: unknown };

/** A valid reference identifier: 14-22 letters/digits. */
const id = (name: string) => name.padEnd(14, "0");

const makeModel = (overrides: ModelOverrides = {}): FastTrackResourceModel =>
  ({
    title: "Titel",
    description: "Beschreibung",
    theme: [],
    resourceTypeGeneral: [],
    spatial: "Berlin",
    resourceCreationMethod: [RESOURCE_CREATION_METHOD],
    accrualPeriodicity: FREQUENCY,
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

/** The `error` of a failed submission result (fails the test if the result is a success). */
function errorOf(result: unknown) {
  const failure = result as { success: boolean; error: SubmissionError<{ $type: string }> };
  expect(failure.success).toBe(false);
  return failure.error;
}

/**
 * Pins the language the service sees, so no test depends on the default language of the project's
 * global test providers. It spies on `getActiveLang` of the real TranslocoService instead of
 * replacing the service: the service only calls `getActiveLang()`.
 */
function mockActiveLang(initial: string) {
  const spy = vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue(initial);
  return { set: (lang: string) => spy.mockReturnValue(lang) };
}

// eslint-disable-next-line max-lines-per-function
describe("FastTrackResourceSubmission", () => {
  let service: FastTrackResourceSubmission;
  let http: HttpTestingController;
  let activeLang: ReturnType<typeof mockActiveLang>;

  const bodyOf = (req: TestRequest) => req.request.body as Body;
  const requestsOfType = (type: string) =>
    http.match((r) => r.url === RULE_SET_URL && (r.body as Body)?.["$type"] === type);
  const personRequests = () => requestsOfType("PersonRuleSetRequest");
  const contactPointRequests = () => requestsOfType("ContactPointRuleSetRequest");
  const resourceRequests = () => requestsOfType("ResourceRuleSetRequest");
  const givenNameOf = (r: TestRequest) =>
    ((bodyOf(r)["additive"] as Body)["givenName"] as string[])[0];
  const fail = (request: TestRequest, status = 500) =>
    request.flush("fail", { status, statusText: "Server Error" });

  /** Submits a model that needs no new items and returns the `additive` part of the POSTed resource. */
  async function sentAdditive(model: FastTrackResourceModel): Promise<Body> {
    const { done } = track(service.submit(model));
    const [request] = resourceRequests();
    const additive = (bodyOf(request)["additive"] ?? {}) as Body;
    request.flush({ $type: "ResourceRuleSetResponse" });
    await done;
    return additive;
  }

  beforeEach(() => {
    service = TestBed.inject(FastTrackResourceSubmission);
    http = TestBed.inject(HttpTestingController);
    activeLang = mockActiveLang("de"); // explicit default, independent of the project's test config
  });

  afterEach(() => {
    // cancelled requests (aborted because a sibling failed) are expected in some tests
    http.verify({ ignoreCancelled: true });
    vi.restoreAllMocks();
  });

  // eslint-disable-next-line max-lines-per-function
  describe("the POSTed resource", () => {
    it("is a ResourceRuleSetRequest with an AdditiveResource", async () => {
      const model = makeModel({});
      const { done } = track(service.submit(model));

      const [request] = resourceRequests();
      expect(request.request.method).toBe("POST");
      expect(bodyOf(request)["$type"]).toBe("ResourceRuleSetRequest");
      expect((bodyOf(request)["additive"] as Body)["$type"]).toBe("AdditiveResource");
      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("wraps single-language text fields as { value, language } using the active language", async () => {
      const additive = await sentAdditive(makeModel());

      expect(additive["title"]).toEqual([{ value: "Titel", language: "de" }]);
      expect(additive["description"]).toEqual([{ value: "Beschreibung", language: "de" }]);
      expect(additive["provenance"]).toEqual([{ value: "Herkunft", language: "de" }]);
      expect(additive["rights"]).toEqual([{ value: "Rechte", language: "de" }]);
      expect(additive["spatial"]).toEqual([{ value: "Berlin", language: "de" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "Rechtsgrundlage", language: "de" }]);
    });

    it("tags keywords with their OWN language, regardless of the active language", async () => {
      activeLang.set("en");
      const additive = await sentAdditive(makeModel());

      expect(additive["keyword"]).toEqual([
        { value: "Gesundheit", language: "de" },
        { value: "health", language: "en" },
      ]);
    });

    it("emits German keywords before English ones, each list in its original order", async () => {
      const additive = await sentAdditive(
        makeModel({ keywords: { de: ["a", "b"], en: ["x", "y"] } }),
      );

      expect((additive["keyword"] as { value: string }[]).map((k) => k.value)).toEqual([
        "a",
        "b",
        "x",
        "y",
      ]);
    });

    it("passes the identifiers of existing reference items through, in order", async () => {
      const additive = await sentAdditive(
        makeModel({
          contact: [previewPerson(id("contact1"))],
          contributor: [previewPerson(id("person1")), previewPerson(id("person2"))],
          unitInCharge: [previewUnit(id("unit1"))],
          creator: [previewPerson(id("person3"))],
          contributingUnit: [previewUnit(id("unit2"))],
        }),
      );

      expect(additive["contact"]).toEqual([id("contact1")]);
      expect(additive["contributor"]).toEqual([id("person1"), id("person2")]);
      expect(additive["unitInCharge"]).toEqual([id("unit1")]);
      expect(additive["creator"]).toEqual([id("person3")]);
      expect(additive["contributingUnit"]).toEqual([id("unit2")]);
    });

    it("sends empty reference lists as empty arrays", async () => {
      const additive = await sentAdditive(makeModel());

      expect(additive["contact"]).toEqual([]);
      expect(additive["contributor"]).toEqual([]);
      expect(additive["unitInCharge"]).toEqual([]);
      expect(additive["creator"]).toEqual([]);
      expect(additive["contributingUnit"]).toEqual([]);
    });

    it("passes vocabulary values through as-is", async () => {
      const additive = await sentAdditive(
        makeModel({
          theme: [THEME],
          resourceTypeGeneral: [RESOURCE_TYPE_GENERAL],
          resourceCreationMethod: [RESOURCE_CREATION_METHOD],
          accrualPeriodicity: FREQUENCY,
        }),
      );

      expect(additive["theme"]).toEqual([THEME]);
      expect(additive["resourceTypeGeneral"]).toEqual([RESOURCE_TYPE_GENERAL]);
      expect(additive["resourceCreationMethod"]).toEqual([RESOURCE_CREATION_METHOD]);
      expect(additive["accrualPeriodicity"]).toBe(FREQUENCY);
    });

    it("formats start/end as ISO dates (date only, no time)", async () => {
      const additive = await sentAdditive(
        makeModel({
          start: DateTime.fromISO("2026-01-05T23:30:00"),
          end: DateTime.fromISO("2026-12-31T00:00:00"),
        }),
      );

      expect(additive["start"]).toEqual(["2026-01-05"]);
      expect(additive["end"]).toEqual(["2026-12-31"]);
    });

    it("checks start/end are empty arrays when they are not set", async () => {
      const additive = await sentAdditive(makeModel({ start: null, end: null }));

      expect(additive["start"]).toEqual([]);
      expect(additive["end"]).toEqual([]);
    });

    it("still submits when the optional texts (spatial, hasLegalBasis) are empty", async () => {
      const result = await service.submit(makeModel({ spatial: "", hasLegalBasis: "" }));
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.response.additive?.spatial?.length).toBe(0);
        expect(result.response.additive?.hasLegalBasis?.length).toBe(0);
      }
    });
  });

  describe("language", () => {
    const languageOfTitle = (additive: Body) =>
      (additive["title"] as { language: string }[])[0].language;

    it("uses German texts when the active language is 'de'", async () => {
      activeLang.set("de");

      expect(languageOfTitle(await sentAdditive(makeModel()))).toBe("de");
    });

    it("uses English texts when the active language is 'en'", async () => {
      activeLang.set("en");
      const additive = await sentAdditive(makeModel());

      expect(additive["title"]).toEqual([{ value: "Titel", language: "en" }]);
      expect(additive["description"]).toEqual([{ value: "Beschreibung", language: "en" }]);
      expect(additive["provenance"]).toEqual([{ value: "Herkunft", language: "en" }]);
      expect(additive["rights"]).toEqual([{ value: "Rechte", language: "en" }]);
      expect(additive["spatial"]).toEqual([{ value: "Berlin", language: "en" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "Rechtsgrundlage", language: "en" }]);
    });

    it.each(["fr", "", "EN", "0", "length"])(
      "falls back to German for the unsupported language '%s'",
      async (lang) => {
        activeLang.set(lang);

        expect(languageOfTitle(await sentAdditive(makeModel()))).toBe("de");
      },
    );
  });

  describe("submit: resource without any new reference items", () => {
    it("sends exactly one request and resolves with the response", async () => {
      const model = makeModel({
        contact: [previewPerson(id("contact1"))],
        unitInCharge: [previewUnit(id("unit1"))],
      });

      const { state, done } = track(service.submit(model));

      expect(personRequests()).toHaveLength(0);
      expect(contactPointRequests()).toHaveLength(0);
      const [request] = resourceRequests();
      const response = { $type: "ResourceRuleSetResponse", stableTargetId: id("resource1") };
      request.flush(response);
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toEqual({ success: true, response });
    });
  });

  // eslint-disable-next-line max-lines-per-function
  describe("submit: creating new reference items first", () => {
    it("posts a new Person as a PersonRuleSetRequest and uses the returned stableTargetId", async () => {
      const { state, done } = track(
        service.submit(makeModel({ creator: [createPerson("Jane", "Doe")] })),
      );

      const [request] = personRequests();
      expect(request.request.method).toBe("POST");
      expect(bodyOf(request)).toEqual({
        $type: "PersonRuleSetRequest",
        additive: { $type: "AdditivePerson", givenName: ["Jane"], familyName: ["Doe"] },
      });
      request.flush({ stableTargetId: id("newperson1") });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["creator"]).toEqual([
        id("newperson1"),
      ]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;

      expect(state.value).toMatchObject({ success: true });
    });

    it("posts a new ContactPoint as a ContactPointRuleSetRequest (email as a list) and uses the returned stableTargetId", async () => {
      const { done } = track(
        service.submit(makeModel({ contact: [createContactPoint("info@example.org")] })),
      );

      const [request] = contactPointRequests();
      expect(bodyOf(request)).toEqual({
        $type: "ContactPointRuleSetRequest",
        additive: { $type: "AdditiveContactPoint", email: ["info@example.org"] },
      });
      request.flush({ stableTargetId: id("newcontact1") });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["contact"]).toEqual([
        id("newcontact1"),
      ]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("uses the same '$type' key for every request it sends (resource, person, contact point)", async () => {
      const model = makeModel({ contact: [createContactPoint()], creator: [createPerson()] });
      const { done } = track(service.submit(model));

      const [person] = personRequests();
      const [contactPoint] = contactPointRequests();
      for (const request of [person, contactPoint]) {
        expect(bodyOf(request)).not.toHaveProperty("entityType");
        expect((bodyOf(request)["additive"] as Body)["$type"]).toBeDefined();
      }
      person.flush({ stableTargetId: id("person1") });
      contactPoint.flush({ stableTargetId: id("contact1") });
      const [resourceRequest] = resourceRequests();
      expect(bodyOf(resourceRequest)).not.toHaveProperty("entityType");
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("does not send the resource until EVERY new item has been answered", async () => {
      const { done } = track(
        service.submit(makeModel({ contact: [createContactPoint()], creator: [createPerson()] })),
      );

      const [person] = personRequests();
      const [contactPoint] = contactPointRequests();

      person.flush({ stableTargetId: id("person1") });
      expect(resourceRequests()).toHaveLength(0); // contact point still outstanding
      expect(contactPoint.cancelled).toBe(false); // control: a pending sibling is NOT aborted normally

      contactPoint.flush({ stableTargetId: id("contact1") });
      const [resourceRequest] = resourceRequests();
      expect(resourceRequest).toBeDefined();

      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("keeps the original list order in the result, no matter in which order the answers arrive", async () => {
      const model = makeModel({
        contributor: [
          previewPerson(id("existing1")),
          createPerson("A", "One"),
          createPerson("B", "Two"),
        ],
      });
      const { done } = track(service.submit(model));

      const requests = personRequests();
      expect(requests).toHaveLength(2);
      // answer B first, then A
      requests.find((r) => givenNameOf(r) === "B")!.flush({ stableTargetId: id("idforb") });
      requests.find((r) => givenNameOf(r) === "A")!.flush({ stableTargetId: id("idfora") });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["contributor"]).toEqual([
        id("existing1"),
        id("idfora"),
        id("idforb"),
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

      const [contactPoint] = contactPointRequests();
      const requests = personRequests();
      expect(requests).toHaveLength(2);
      requests.find((r) => givenNameOf(r) === "C")!.flush({ stableTargetId: id("creator1") });
      requests.find((r) => givenNameOf(r) === "D")!.flush({ stableTargetId: id("contrib1") });
      expect(resourceRequests()).toHaveLength(0); // the contact point is still outstanding
      contactPoint.flush({ stableTargetId: id("contact1") });

      const [resourceRequest] = resourceRequests();
      const additive = (bodyOf(resourceRequest)["additive"] ?? {}) as Body;
      expect(additive["creator"]).toEqual([id("creator1")]);
      expect(additive["contributor"]).toEqual([id("contrib1")]);
      expect(additive["contact"]).toEqual([id("contact1")]);
      resourceRequest.flush({ $type: "ResourceRuleSetResponse" });
      await done;

      expect(state.value).toMatchObject({ success: true });
    });
  });

  describe("submit: the resource request itself fails", () => {
    it("resolves (does not reject) with success:false and a SubmissionError holding the payload that was sent and the HTTP error", async () => {
      const { state, done } = track(
        service.submit(makeModel({ contact: [previewPerson(id("contact1"))] })),
      );

      const [request] = resourceRequests();
      fail(request);
      await done;

      expect(state.status).toBe("resolved");
      const error = errorOf(state.value);
      expect(error).toBeInstanceOf(SubmissionError);
      expect(error.message).toBe("Error while submitting 'ResourceRuleSetRequest'");
      expect(error.payload["$type"]).toBe("ResourceRuleSetRequest");
      expect(error.payload).toEqual(bodyOf(request));
      expect(error.innerError).toBeInstanceOf(HttpErrorResponse);
      expect(error.innerError).toMatchObject({ status: 500 });
    });

    it("reports a network error (status 0) the same way", async () => {
      const { state, done } = track(service.submit(makeModel()));

      resourceRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("resolved");
      expect(errorOf(state.value).innerError).toMatchObject({ status: 0 });
    });

    it("still contains the ids of items that were already created before the failure", async () => {
      const { state, done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      personRequests()[0].flush({ stableTargetId: id("person1") });
      fail(resourceRequests()[0], 422);
      await done;

      const payload = errorOf(state.value).payload as unknown as { additive: Body };
      expect(payload.additive["creator"]).toEqual([id("person1")]);
    });
  });

  // eslint-disable-next-line max-lines-per-function
  describe("submit: creating a new item fails", () => {
    // Like a failing resource request, this resolves with success:false and a SubmissionError.
    // Its payload is the request of the new item that failed (not the resource).

    it.each([
      [
        "contact",
        { contact: [createContactPoint("kaputt@example.org")] },
        "ContactPointRuleSetRequest",
      ],
      ["creator", { creator: [createPerson("Kaputt", "Person")] }, "PersonRuleSetRequest"],
      ["contributor", { contributor: [createPerson("Kaputt", "Person")] }, "PersonRuleSetRequest"],
    ] as [string, ModelOverrides, string][])(
      "resolves with success:false and a SubmissionError holding the failed request and the HTTP error ('%s')",
      async (_list, overrides, type) => {
        const { state, done } = track(service.submit(makeModel(overrides)));

        const [request] = [...personRequests(), ...contactPointRequests()];
        fail(request);
        await done;

        expect(state.status).toBe("resolved");
        const error = errorOf(state.value);
        expect(error).toBeInstanceOf(SubmissionError);
        expect(error.message).toBe(`Error while submitting '${type}'`);
        expect(error.payload).toEqual(bodyOf(request)); // the request that failed
        expect(error.innerError).toBeInstanceOf(HttpErrorResponse);
        expect(error.innerError).toMatchObject({ status: 500 });
      },
    );

    it("never sends the resource when a new item failed", async () => {
      const { done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      fail(personRequests()[0]);
      await done;

      expect(resourceRequests()).toHaveLength(0);
    });

    it("reports a network error (status 0) the same way", async () => {
      const { state, done } = track(service.submit(makeModel({ contact: [createContactPoint()] })));

      contactPointRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(errorOf(state.value)).toBeInstanceOf(SubmissionError);
      expect(errorOf(state.value).innerError).toMatchObject({ status: 0 });
    });

    it("cancels the new-item requests that are still in flight when one of them fails", async () => {
      const model = makeModel({
        contact: [createContactPoint()],
        creator: [createPerson("A", "One")],
        contributor: [createPerson("B", "Two")],
      });
      const { state, done } = track(service.submit(model));

      const requests = personRequests();
      const [contactPoint] = contactPointRequests();
      expect(requests).toHaveLength(2);

      fail(contactPoint);
      await done;

      expect(state.value).toMatchObject({ success: false });
      expect(requests[0].cancelled).toBe(true);
      expect(requests[1].cancelled).toBe(true);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("names the request of the item that failed when several were sent (here: the second person)", async () => {
      const model = makeModel({
        creator: [createPerson("Erste", "Person"), createPerson("Zweite", "Person")],
      });
      const { state, done } = track(service.submit(model));

      const requests = personRequests();
      requests.find((r) => givenNameOf(r) === "Erste")!.flush({ stableTargetId: id("person1") });
      const second = requests.find((r) => givenNameOf(r) === "Zweite")!;
      fail(second, 503);
      await done;

      const error = errorOf(state.value);
      expect(error.payload).toEqual(bodyOf(second));
      expect(error.innerError).toMatchObject({ status: 503 });
    });

    it("fails the whole submission even though another item was already created, which stays on the backend (no rollback)", async () => {
      const model = makeModel({
        creator: [createPerson("A", "One")],
        contact: [createContactPoint()],
      });
      const { state, done } = track(service.submit(model));

      const [person] = personRequests();
      const [contactPoint] = contactPointRequests();

      person.flush({ stableTargetId: id("person1") }); // already persisted on the backend
      fail(contactPoint, 503);
      await done;

      expect(state.value).toMatchObject({ success: false });
      expect(resourceRequests()).toHaveLength(0);
      // no compensating request (e.g. a delete) is sent for the person that was already created
      http.expectNone((r) => r.method !== "POST");
    });

    it("reports only the first failure if several new items fail", async () => {
      const model = makeModel({ creator: [createPerson("A", "One"), createPerson("B", "Two")] });
      const { state, done } = track(service.submit(model));

      const [first, second] = personRequests();
      fail(first, 500);
      await done;

      expect(second.cancelled).toBe(true); // the second never gets to fail separately
      expect(errorOf(state.value).innerError).toMatchObject({ status: 500 });
    });

    it("treats a response without stableTargetId as a failure of that item", async () => {
      const { state, done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      const [request] = personRequests();
      request.flush({});
      await done;

      expect(state.status).toBe("resolved");
      const error = errorOf(state.value);
      expect(error).toBeInstanceOf(SubmissionError);
      expect(error.payload).toEqual(bodyOf(request));
      expect(error.innerError?.message).toBe("No stableTargetId in response.");
      expect(resourceRequests()).toHaveLength(0); // no resource with an `undefined` id gets sent
    });

    it("treats an empty response body (null) as a failure of that item as well", async () => {
      const { state, done } = track(service.submit(makeModel({ contact: [createContactPoint()] })));

      contactPointRequests()[0].flush(null);
      await done;

      expect(state.status).toBe("resolved");
      expect(errorOf(state.value)).toBeInstanceOf(SubmissionError);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("stays usable after a failed submit (no state carried over)", async () => {
      const failing = track(service.submit(makeModel({ creator: [createPerson()] })));
      fail(personRequests()[0]);
      await failing.done;
      expect(failing.state.value).toMatchObject({ success: false });

      const retry = track(service.submit(makeModel({ creator: [createPerson()] })));
      personRequests()[0].flush({ stableTargetId: id("person2") });
      resourceRequests()[0].flush({ $type: "ResourceRuleSetResponse" });
      await retry.done;

      expect(retry.state.value).toMatchObject({ success: true });
    });

    it("returns success:false (does not reject) when the data of a new item is invalid", async () => {
      const { state, done } = track(
        service.submit(makeModel({ contact: [createContactPoint("not-an-email")] })),
      );
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toMatchObject({ success: false });
    });
  });
});
