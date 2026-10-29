import { HttpErrorResponse } from "@angular/common/http";
import { HttpTestingController, type TestRequest } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { TranslocoService } from "@jsverse/transloco";
import { vi } from "vitest";

import {
  type FastTrackResourceModel,
  FastTrackResourceSubPostError,
} from "./fast-track-resource.models";
import { FastTrackResourceSubmission } from "./fast-track-resource-submission";

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

/** Everything an error object holds: own properties, including non-enumerable ones like `cause`. */
const carried = (error: unknown): unknown[] =>
  Object.getOwnPropertyNames(error).map((key) => (error as Record<string, unknown>)[key]);

// eslint-disable-next-line max-lines-per-function
describe("FastTrackResourceSubmission", () => {
  let service: FastTrackResourceSubmission;
  let http: HttpTestingController;

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
    const transloco = TestBed.inject(TranslocoService);
    vi.spyOn(transloco, "getActiveLang").mockReturnValue("de");

    service = TestBed.inject(FastTrackResourceSubmission);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // cancelled requests (aborted because a sibling failed) are expected in some tests
    http.verify({ ignoreCancelled: true });
    vi.restoreAllMocks();
  });

  describe("the POSTed resource", () => {
    it("is a ResourceRuleSetRequest with an AdditiveResource", async () => {
      const { done } = track(service.submit(makeModel()));

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
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("en");
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
          contact: [previewPerson("contact-1")],
          contributor: [previewPerson("person-1"), previewPerson("person-2")],
          unitInCharge: [previewUnit("unit-1")],
          creator: [previewPerson("person-3")],
          contributingUnit: [previewUnit("unit-2")],
        }),
      );

      expect(additive["contact"]).toEqual(["contact-1"]);
      expect(additive["contributor"]).toEqual(["person-1", "person-2"]);
      expect(additive["unitInCharge"]).toEqual(["unit-1"]);
      expect(additive["creator"]).toEqual(["person-3"]);
      expect(additive["contributingUnit"]).toEqual(["unit-2"]);
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
          theme: ["theme-1"],
          resourceCreationMethod: ["method-1"],
          accrualPeriodicity: "freq-1",
        }),
      );

      expect(additive["theme"]).toEqual(["theme-1"]);
      expect(additive["resourceCreationMethod"]).toEqual(["method-1"]);
      expect(additive["accrualPeriodicity"]).toBe("freq-1");
    });

    it("sends start/end exactly as the datepicker value strings", async () => {
      const additive = await sentAdditive(
        makeModel({ start: "2026-01-05", end: "2026-12-31T10:00:00Z" }),
      );

      expect(additive["start"]).toEqual(["2026-01-05"]);
      expect(additive["end"]).toEqual(["2026-12-31T10:00:00Z"]);
    });

    it("leaves start/end undefined when they are not set", async () => {
      const additive = await sentAdditive(makeModel({ start: null, end: null }));

      expect(additive["start"]).toBeUndefined();
      expect(additive["end"]).toBeUndefined();
    });

    // Documents what happens today, it does not say this is right: optional texts that were left
    // empty are sent as an empty text instead of being omitted. If the backend rejects empty
    // texts, this is where to change it (and then this test).
    it("currently sends empty optional texts (spatial, hasLegalBasis) as empty texts", async () => {
      const additive = await sentAdditive(makeModel({ spatial: "", hasLegalBasis: "" }));

      expect(additive["spatial"]).toEqual([{ value: "", language: "de" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "", language: "de" }]);
    });
  });

  describe("language", () => {
    const languageOfTitle = (additive: Body) =>
      (additive["title"] as { language: string }[])[0].language;

    it("uses German texts when the active language is 'de'", async () => {
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("de");

      expect(languageOfTitle(await sentAdditive(makeModel()))).toBe("de");
    });

    it("uses English texts when the active language is 'en'", async () => {
      vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue("en");
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
        vi.spyOn(TestBed.inject(TranslocoService), "getActiveLang").mockReturnValue(lang);

        expect(languageOfTitle(await sentAdditive(makeModel()))).toBe("de");
      },
    );
  });

  describe("submit: resource without any new reference items", () => {
    it("sends exactly one request and resolves with the response", async () => {
      const model = makeModel({
        contact: [previewPerson("contact-1")],
        unitInCharge: [previewUnit("unit-1")],
      });

      const { state, done } = track(service.submit(model));

      expect(personRequests()).toHaveLength(0);
      expect(contactPointRequests()).toHaveLength(0);
      const [request] = resourceRequests();
      const response = { $type: "ResourceRuleSetResponse", stableTargetId: "res-1" };
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
      request.flush({ stableTargetId: "newPerson0001" });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["creator"]).toEqual([
        "newPerson0001",
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
      request.flush({ stableTargetId: "newContact001" });

      const [resourceRequest] = resourceRequests();
      expect(((bodyOf(resourceRequest)["additive"] ?? {}) as Body)["contact"]).toEqual([
        "newContact001",
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
      person.flush({ stableTargetId: "person00000001" });
      contactPoint.flush({ stableTargetId: "contact0000001" });
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

      person.flush({ stableTargetId: "person00000001" });
      expect(resourceRequests()).toHaveLength(0); // contact point still outstanding
      expect(contactPoint.cancelled).toBe(false); // control: a pending sibling is NOT aborted normally

      contactPoint.flush({ stableTargetId: "contact0000001" });
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

      const requests = personRequests();
      expect(requests).toHaveLength(2);
      // answer B first, then A
      requests.find((r) => givenNameOf(r) === "B")!.flush({ stableTargetId: "id-for-B" });
      requests.find((r) => givenNameOf(r) === "A")!.flush({ stableTargetId: "id-for-A" });

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

      const [contactPoint] = contactPointRequests();
      const requests = personRequests();
      expect(requests).toHaveLength(2);
      requests.find((r) => givenNameOf(r) === "C")!.flush({ stableTargetId: "creator000001" });
      requests.find((r) => givenNameOf(r) === "D")!.flush({ stableTargetId: "contrib000001" });
      expect(resourceRequests()).toHaveLength(0); // the contact point is still outstanding
      contactPoint.flush({ stableTargetId: "contact000001" });

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
      fail(request);
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

      resourceRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toMatchObject({ success: false, error: { status: 0 } });
    });

    it("still contains the ids of items that were already created before the failure", async () => {
      const { state, done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      personRequests()[0].flush({ stableTargetId: "person00000001" });
      fail(resourceRequests()[0], 422);
      await done;

      const payload = (state.value as unknown as { payload: { additive: Body } }).payload;
      expect(payload.additive["creator"]).toEqual(["person00000001"]);
    });
  });

  // eslint-disable-next-line max-lines-per-function
  describe("submit: creating a new item fails", () => {
    // NOTE: unlike a failing resource request (which resolves with success:false), a failing new
    // item makes submit() REJECT with a FastTrackResourceSubPostError -- nothing in submit()
    // catches it. Callers must catch it (and the resolved success:false) separately.

    it.each([
      [
        "contact",
        { contact: [createContactPoint("kaputt@example.org")] },
        "ContactPointRuleSetRequest",
      ],
      ["creator", { creator: [createPerson("Kaputt", "Person")] }, "PersonRuleSetRequest"],
      ["contributor", { contributor: [createPerson("Kaputt", "Person")] }, "PersonRuleSetRequest"],
    ] as [string, ModelOverrides, string][])(
      "rejects with a FastTrackResourceSubPostError holding the HTTP error and the failed request ('%s')",
      async (_list, overrides, type) => {
        const { state, done } = track(service.submit(makeModel(overrides)));

        const [request] = [...personRequests(), ...contactPointRequests()];
        fail(request);
        await done;

        expect(state.status).toBe("rejected");
        expect(state.error).toBeInstanceOf(FastTrackResourceSubPostError);
        const held = carried(state.error);
        expect(held).toContainEqual(bodyOf(request)); // the request that failed
        expect(bodyOf(request)["$type"]).toBe(type);
        expect(held.some((v) => v instanceof HttpErrorResponse && v.status === 500)).toBe(true);
      },
    );

    it("never sends the resource when a new item failed", async () => {
      const { done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      fail(personRequests()[0]);
      await done;

      expect(resourceRequests()).toHaveLength(0);
    });

    it("rejects with a network error (status 0) the same way", async () => {
      const { state, done } = track(service.submit(makeModel({ contact: [createContactPoint()] })));

      contactPointRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(state.error).toBeInstanceOf(FastTrackResourceSubPostError);
      expect(
        carried(state.error).some((v) => v instanceof HttpErrorResponse && v.status === 0),
      ).toBe(true);
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

      expect(state.status).toBe("rejected");
      expect(requests[0].cancelled).toBe(true);
      expect(requests[1].cancelled).toBe(true);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("holds the request of the item that failed when several were sent (here: the second person)", async () => {
      const model = makeModel({
        creator: [createPerson("Erste", "Person"), createPerson("Zweite", "Person")],
      });
      const { state, done } = track(service.submit(model));

      const requests = personRequests();
      requests.find((r) => givenNameOf(r) === "Erste")!.flush({ stableTargetId: "person00000001" });
      const second = requests.find((r) => givenNameOf(r) === "Zweite")!;
      fail(second, 503);
      await done;

      const held = carried(state.error);
      expect(held).toContainEqual(bodyOf(second));
      expect(held.some((v) => v instanceof HttpErrorResponse && v.status === 503)).toBe(true);
    });

    it("rejects even though another item was already created, which stays on the backend (no rollback)", async () => {
      const model = makeModel({
        creator: [createPerson("A", "One")],
        contact: [createContactPoint()],
      });
      const { state, done } = track(service.submit(model));

      const [person] = personRequests();
      const [contactPoint] = contactPointRequests();

      person.flush({ stableTargetId: "person00000001" }); // already persisted on the backend
      fail(contactPoint, 503);
      await done;

      expect(state.status).toBe("rejected");
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
      expect(
        carried(state.error).some((v) => v instanceof HttpErrorResponse && v.status === 500),
      ).toBe(true);
    });

    it("treats a response without stableTargetId as a failure of that item", async () => {
      const { state, done } = track(service.submit(makeModel({ creator: [createPerson()] })));

      const [request] = personRequests();
      request.flush({});
      await done;

      expect(state.status).toBe("rejected");
      expect(state.error).toBeInstanceOf(FastTrackResourceSubPostError);
      const held = carried(state.error);
      expect(held).toContainEqual(bodyOf(request));
      expect(
        held.some((v) => v instanceof Error && v.message === "No stableTargetId in response."),
      ).toBe(true);
      expect(resourceRequests()).toHaveLength(0); // no resource with an `undefined` id gets sent
    });

    it("treats an empty response body (null) as a failure of that item as well", async () => {
      const { state, done } = track(service.submit(makeModel({ contact: [createContactPoint()] })));

      contactPointRequests()[0].flush(null);
      await done;

      expect(state.error).toBeInstanceOf(FastTrackResourceSubPostError);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("stays usable after a failed submit (no state carried over)", async () => {
      const failing = track(service.submit(makeModel({ creator: [createPerson()] })));
      fail(personRequests()[0]);
      await failing.done;
      expect(failing.state.status).toBe("rejected");

      const retry = track(service.submit(makeModel({ creator: [createPerson()] })));
      personRequests()[0].flush({ stableTargetId: "person00000002" });
      resourceRequests()[0].flush({ $type: "ResourceRuleSetResponse" });
      await retry.done;

      expect(retry.state.value).toMatchObject({ success: true });
    });
  });
});
