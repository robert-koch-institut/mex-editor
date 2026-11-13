import { HttpErrorResponse } from "@angular/common/http";
import { HttpTestingController, type TestRequest } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { TranslocoService } from "@jsverse/transloco";
import { vi } from "vitest";

import { SubmissionError } from "../shared/models/submission-result";
import type { FastTrackActivityModel } from "./fast-track-activity.model";
import type { FastTrackResourceModel } from "./fast-track-resource.models";
import { FastTrackSubmission } from "./fast-track-submission";

const RULE_SET_URL = "api/v0/backend/rule-set";

const THEME = "https://mex.rki.de/item/theme-1";
const RESOURCE_CREATION_METHOD = "https://mex.rki.de/item/resource-creation-method-1";
const FREQUENCY = "https://mex.rki.de/item/frequency-1";

type Body = Record<string, unknown>;
type ResourceModelOverrides = { [K in keyof FastTrackResourceModel]?: unknown };

/** A valid reference identifier: 14-22 letters/digits. */
const id = (name: string) => name.padEnd(14, "0");

const makeResourceModel = (overrides: ResourceModelOverrides = {}): FastTrackResourceModel =>
  ({
    $type: "FastTrackResourceModel",
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

type ActivityModelOverrides = {
  [K in keyof FastTrackActivityModel]?: unknown;
};

const makeActivityModel = (overrides: ActivityModelOverrides = {}): FastTrackActivityModel =>
  ({
    $type: "FastTrackActivityModel",
    title: "Aktivität",
    abstract: "Beschreibung der Aktivität",
    contact: [previewPerson(id("contact1"))],
    responsibleUnit: [previewUnit(id("unit1"))],
    activityType: [],
    shortName: "Kurzname",
    involvedPerson: [],
    involvedUnit: [],
    start: null,
    end: null,
    funderOrCommissioner: [],
    website: [],
    ...overrides,
  }) as unknown as FastTrackActivityModel;

const createOrganization = (officialName = "Organisation") => ({
  $type: "CreateOrganization",
  officialName,
});

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
describe("FasttrackSubmission", () => {
  let service: FastTrackSubmission;
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

  const activityRequests = () => requestsOfType("ActivityRuleSetRequest");
  const organizationRequests = () => requestsOfType("OrganizationRuleSetRequest");
  const activityAdditive = (request: TestRequest) => (bodyOf(request)["additive"] ?? {}) as Body;

  async function sentActivityAdditive(model: FastTrackActivityModel): Promise<Body> {
    const { done } = track(service.submit(model));
    const [request] = activityRequests();
    const additive = activityAdditive(request);
    request.flush({ $type: "ActivityRuleSetResponse" });
    await done;
    return additive;
  }

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
    service = TestBed.inject(FastTrackSubmission);
    http = TestBed.inject(HttpTestingController);
    activeLang = mockActiveLang("de"); // explicit default, independent of the project's test config
  });

  afterEach(() => {
    // cancelled requests (aborted because a sibling failed) are expected in some tests
    http.verify({ ignoreCancelled: true });
    vi.restoreAllMocks();
  });

  describe("the POSTed resource", () => {
    it("is a ResourceRuleSetRequest with an AdditiveResource", async () => {
      const model = makeResourceModel({});
      const { done } = track(service.submit(model));

      const [request] = resourceRequests();
      expect(request.request.method).toBe("POST");
      expect(bodyOf(request)["$type"]).toBe("ResourceRuleSetRequest");
      expect((bodyOf(request)["additive"] as Body)["$type"]).toBe("AdditiveResource");
      request.flush({ $type: "ResourceRuleSetResponse" });
      await done;
    });

    it("wraps single-language text fields as { value, language } using the active language", async () => {
      const additive = await sentAdditive(makeResourceModel());

      expect(additive["title"]).toEqual([{ value: "Titel", language: "de" }]);
      expect(additive["description"]).toEqual([{ value: "Beschreibung", language: "de" }]);
      expect(additive["provenance"]).toEqual([{ value: "Herkunft", language: "de" }]);
      expect(additive["rights"]).toEqual([{ value: "Rechte", language: "de" }]);
      expect(additive["spatial"]).toEqual([{ value: "Berlin", language: "de" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "Rechtsgrundlage", language: "de" }]);
    });

    it("tags keywords with their OWN language, regardless of the active language", async () => {
      activeLang.set("en");
      const additive = await sentAdditive(makeResourceModel());

      expect(additive["keyword"]).toEqual([
        { value: "Gesundheit", language: "de" },
        { value: "health", language: "en" },
      ]);
    });

    it("emits German keywords before English ones, each list in its original order", async () => {
      const additive = await sentAdditive(
        makeResourceModel({ keywords: { de: ["a", "b"], en: ["x", "y"] } }),
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
        makeResourceModel({
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
      const additive = await sentAdditive(makeResourceModel());

      expect(additive["contact"]).toEqual([]);
      expect(additive["contributor"]).toEqual([]);
      expect(additive["unitInCharge"]).toEqual([]);
      expect(additive["creator"]).toEqual([]);
      expect(additive["contributingUnit"]).toEqual([]);
    });

    it("passes vocabulary values through as-is", async () => {
      const additive = await sentAdditive(
        makeResourceModel({
          theme: [THEME],
          resourceCreationMethod: [RESOURCE_CREATION_METHOD],
          accrualPeriodicity: FREQUENCY,
        }),
      );

      expect(additive["theme"]).toEqual([THEME]);
      expect(additive["resourceCreationMethod"]).toEqual([RESOURCE_CREATION_METHOD]);
      expect(additive["accrualPeriodicity"]).toBe(FREQUENCY);
    });

    it("sends start/end exactly as the datepicker value strings", async () => {
      const additive = await sentAdditive(
        makeResourceModel({ start: "2026-01-05", end: "2026-12-31T10:00:00Z" }),
      );

      expect(additive["start"]).toEqual(["2026-01-05"]);
      expect(additive["end"]).toEqual(["2026-12-31T10:00:00Z"]);
    });

    it("leaves start/end an empty list when they are not set", async () => {
      const additive = await sentAdditive(makeResourceModel({ start: null, end: null }));

      expect(additive["start"]).toEqual([]);
      expect(additive["end"]).toEqual([]);
    });

    it("checks submitting empty spatial and hasLegalBasis are empty array when not set", async () => {
      const additive = await sentAdditive(makeResourceModel({ spatial: "", hasLegalBasis: "" }));

      expect(additive["spatial"]).toEqual([]);
      expect(additive["hasLegalBasis"]).toEqual([]);
    });
  });

  describe("language", () => {
    const languageOfTitle = (additive: Body) =>
      (additive["title"] as { language: string }[])[0].language;

    it("uses German texts when the active language is 'de'", async () => {
      activeLang.set("de");

      expect(languageOfTitle(await sentAdditive(makeResourceModel()))).toBe("de");
    });

    it("uses English texts when the active language is 'en'", async () => {
      activeLang.set("en");
      const additive = await sentAdditive(makeResourceModel());

      expect(additive["title"]).toEqual([{ value: "Titel", language: "en" }]);
      expect(additive["description"]).toEqual([{ value: "Beschreibung", language: "en" }]);
      expect(additive["provenance"]).toEqual([{ value: "Herkunft", language: "en" }]);
      expect(additive["rights"]).toEqual([{ value: "Rechte", language: "en" }]);
      expect(additive["spatial"]).toEqual([{ value: "Berlin", language: "en" }]);
      expect(additive["hasLegalBasis"]).toEqual([{ value: "Rechtsgrundlage", language: "en" }]);
    });

    it.each(["it", "", "EN", "0", "length"])(
      "falls back to German for the unsupported language '%s'",
      async (lang) => {
        activeLang.set(lang);

        expect(languageOfTitle(await sentAdditive(makeResourceModel()))).toBe("de");
      },
    );
  });

  describe("submit: resource without any new reference items", () => {
    it("sends exactly one request and resolves with the response", async () => {
      const model = makeResourceModel({
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
        service.submit(makeResourceModel({ creator: [createPerson("Jane", "Doe")] })),
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
        service.submit(makeResourceModel({ contact: [createContactPoint("info@example.org")] })),
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
      const model = makeResourceModel({
        contact: [createContactPoint()],
        creator: [createPerson()],
      });
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
        service.submit(
          makeResourceModel({ contact: [createContactPoint()], creator: [createPerson()] }),
        ),
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
      const model = makeResourceModel({
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
      const model = makeResourceModel({
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
        service.submit(makeResourceModel({ contact: [previewPerson(id("contact1"))] })),
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
      const { state, done } = track(service.submit(makeResourceModel()));

      resourceRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("resolved");
      expect(errorOf(state.value).innerError).toMatchObject({ status: 0 });
    });

    it("still contains the ids of items that were already created before the failure", async () => {
      const { state, done } = track(
        service.submit(makeResourceModel({ creator: [createPerson()] })),
      );

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
    ] as [string, ResourceModelOverrides, string][])(
      "resolves with success:false and a SubmissionError holding the failed request and the HTTP error ('%s')",
      async (_list, overrides, type) => {
        const { state, done } = track(service.submit(makeResourceModel(overrides)));

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
      const { done } = track(service.submit(makeResourceModel({ creator: [createPerson()] })));

      fail(personRequests()[0]);
      await done;

      expect(resourceRequests()).toHaveLength(0);
    });

    it("reports a network error (status 0) the same way", async () => {
      const { state, done } = track(
        service.submit(makeResourceModel({ contact: [createContactPoint()] })),
      );

      contactPointRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(errorOf(state.value)).toBeInstanceOf(SubmissionError);
      expect(errorOf(state.value).innerError).toMatchObject({ status: 0 });
    });

    it("cancels the new-item requests that are still in flight when one of them fails", async () => {
      const model = makeResourceModel({
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
      const model = makeResourceModel({
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
      const model = makeResourceModel({
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
      const model = makeResourceModel({
        creator: [createPerson("A", "One"), createPerson("B", "Two")],
      });
      const { state, done } = track(service.submit(model));

      const [first, second] = personRequests();
      fail(first, 500);
      await done;

      expect(second.cancelled).toBe(true); // the second never gets to fail separately
      expect(errorOf(state.value).innerError).toMatchObject({ status: 500 });
    });

    it("treats a response without stableTargetId as a failure of that item", async () => {
      const { state, done } = track(
        service.submit(makeResourceModel({ creator: [createPerson()] })),
      );

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
      const { state, done } = track(
        service.submit(makeResourceModel({ contact: [createContactPoint()] })),
      );

      contactPointRequests()[0].flush(null);
      await done;

      expect(state.status).toBe("resolved");
      expect(errorOf(state.value)).toBeInstanceOf(SubmissionError);
      expect(resourceRequests()).toHaveLength(0);
    });

    it("stays usable after a failed submit (no state carried over)", async () => {
      const failing = track(service.submit(makeResourceModel({ creator: [createPerson()] })));
      fail(personRequests()[0]);
      await failing.done;
      expect(failing.state.value).toMatchObject({ success: false });

      const retry = track(service.submit(makeResourceModel({ creator: [createPerson()] })));
      personRequests()[0].flush({ stableTargetId: id("person2") });
      resourceRequests()[0].flush({ $type: "ResourceRuleSetResponse" });
      await retry.done;

      expect(retry.state.value).toMatchObject({ success: true });
    });

    it("returns success:false (does not reject) when the data of a new item is invalid", async () => {
      const { state, done } = track(
        service.submit(makeResourceModel({ contact: [createContactPoint("not-an-email")] })),
      );
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toMatchObject({ success: false });
    });
  });

  describe("the POSTed activity", () => {
    it("is an ActivityRuleSetRequest with an AdditiveActivity", async () => {
      const { done } = track(service.submit(makeActivityModel()));

      expect(resourceRequests()).toHaveLength(0);
      const [request] = activityRequests();

      expect(request.request.method).toBe("POST");
      expect(bodyOf(request)["$type"]).toBe("ActivityRuleSetRequest");
      expect(activityAdditive(request)["$type"]).toBe("AdditiveActivity");

      request.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("wraps title and abstract using the active language", async () => {
      const additive = await sentActivityAdditive(makeActivityModel());

      expect(additive["title"]).toEqual([{ value: "Aktivität", language: "de" }]);
      expect(additive["abstract"]).toEqual([
        { value: "Beschreibung der Aktivität", language: "de" },
      ]);
    });

    it("uses the active language for title and abstract", async () => {
      activeLang.set("en");

      const additive = await sentActivityAdditive(makeActivityModel());

      expect(additive["title"]).toEqual([{ value: "Aktivität", language: "en" }]);
      expect(additive["abstract"]).toEqual([
        { value: "Beschreibung der Aktivität", language: "en" },
      ]);
    });

    it.each(["it", "", "EN", "0", "length"])(
      "falls back to German for unsupported language '%s'",
      async (lang) => {
        activeLang.set(lang);

        const additive = await sentActivityAdditive(makeActivityModel());

        expect((additive["title"] as { language: string }[])[0].language).toBe("de");
      },
    );

    it("maps shortName when provided", async () => {
      const additive = await sentActivityAdditive(makeActivityModel({ shortName: "FAST" }));

      expect(additive["shortName"]).toEqual([{ value: "FAST", language: "de" }]);
    });

    it("leaves shortName empty when it is not a valid text string", async () => {
      const additive = await sentActivityAdditive(makeActivityModel({ shortName: "" }));

      expect(additive["shortName"]).toEqual([]);
    });

    it("maps start and end as lists", async () => {
      const additive = await sentActivityAdditive(
        makeActivityModel({
          start: "2026-01-05",
          end: "2026-12-31T10:00:00Z",
        }),
      );

      expect(additive["start"]).toEqual(["2026-01-05"]);
      expect(additive["end"]).toEqual(["2026-12-31T10:00:00Z"]);
    });

    it("leaves start and end empty when they are not set", async () => {
      const additive = await sentActivityAdditive(makeActivityModel({ start: null, end: null }));

      expect(additive["start"]).toEqual([]);
      expect(additive["end"]).toEqual([]);
    });

    it("passes website and activityType through", async () => {
      // The exact LinkSchema shape is intentionally not assumed here.
      // The empty arrays are valid model values and must remain empty arrays.
      const additive = await sentActivityAdditive(makeActivityModel());

      expect(additive["website"]).toEqual([]);
      expect(additive["activityType"]).toEqual([]);
    });

    it("passes existing reference identifiers through in order", async () => {
      const additive = await sentActivityAdditive(
        makeActivityModel({
          contact: [previewPerson(id("contact1")), previewPerson(id("contact2"))],
          responsibleUnit: [previewUnit(id("unit1"))],
          involvedPerson: [previewPerson(id("person1")), previewPerson(id("person2"))],
          involvedUnit: [previewUnit(id("unit2"))],
        }),
      );

      expect(additive["contact"]).toEqual([id("contact1"), id("contact2")]);
      expect(additive["responsibleUnit"]).toEqual([id("unit1")]);
      expect(additive["involvedPerson"]).toEqual([id("person1"), id("person2")]);
      expect(additive["involvedUnit"]).toEqual([id("unit2")]);
      expect(additive["funderOrCommissioner"]).toEqual([]);
    });

    it("sends empty optional reference lists as empty arrays", async () => {
      const additive = await sentActivityAdditive(makeActivityModel());

      expect(additive["involvedPerson"]).toEqual([]);
      expect(additive["involvedUnit"]).toEqual([]);
      expect(additive["funderOrCommissioner"]).toEqual([]);
    });
  });

  // eslint-disable-next-line max-lines-per-function
  describe("submit: activity with new reference items", () => {
    it("creates a new contact person and uses its stableTargetId", async () => {
      const { done } = track(
        service.submit(makeActivityModel({ contact: [createPerson("Jane", "Doe")] })),
      );

      const [person] = personRequests();
      expect(bodyOf(person)).toEqual({
        $type: "PersonRuleSetRequest",
        additive: {
          $type: "AdditivePerson",
          givenName: ["Jane"],
          familyName: ["Doe"],
        },
      });

      person.flush({ stableTargetId: id("newperson1") });

      const [activity] = activityRequests();
      expect(activityAdditive(activity)["contact"]).toEqual([id("newperson1")]);

      activity.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("creates a new contact point and uses its stableTargetId", async () => {
      const { done } = track(
        service.submit(
          makeActivityModel({
            contact: [createContactPoint("info@example.org")],
          }),
        ),
      );

      const [contact] = contactPointRequests();
      expect(bodyOf(contact)).toEqual({
        $type: "ContactPointRuleSetRequest",
        additive: {
          $type: "AdditiveContactPoint",
          email: ["info@example.org"],
        },
      });

      contact.flush({ stableTargetId: id("newcontact1") });

      const [activity] = activityRequests();
      expect(activityAdditive(activity)["contact"]).toEqual([id("newcontact1")]);

      activity.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("creates involved persons and preserves their original order", async () => {
      const { done } = track(
        service.submit(
          makeActivityModel({
            involvedPerson: [
              previewPerson(id("existing1")),
              createPerson("Alice", "One"),
              createPerson("Bob", "Two"),
            ],
          }),
        ),
      );

      const requests = personRequests();
      expect(requests).toHaveLength(2);

      requests
        .find((r) => givenNameOf(r) === "Bob")!
        .flush({
          stableTargetId: id("person2"),
        });
      requests
        .find((r) => givenNameOf(r) === "Alice")!
        .flush({
          stableTargetId: id("person1"),
        });

      const [activity] = activityRequests();
      expect(activityAdditive(activity)["involvedPerson"]).toEqual([
        id("existing1"),
        id("person1"),
        id("person2"),
      ]);

      activity.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("creates a new organization and uses its stableTargetId", async () => {
      const { done } = track(
        service.submit(
          makeActivityModel({
            funderOrCommissioner: [createOrganization("Forschungsinstitut")],
          }),
        ),
      );

      const [organization] = organizationRequests();

      expect(bodyOf(organization)).toEqual({
        $type: "OrganizationRuleSetRequest",
        additive: {
          $type: "AdditiveOrganization",
          officialName: [{ value: "Forschungsinstitut", language: "de" }],
        },
      });

      organization.flush({ stableTargetId: id("organization1") });

      const [activity] = activityRequests();
      expect(activityAdditive(activity)["funderOrCommissioner"]).toEqual([id("organization1")]);

      activity.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("waits for all new items before submitting the activity", async () => {
      const { done } = track(
        service.submit(
          makeActivityModel({
            contact: [createContactPoint()],
            involvedPerson: [createPerson()],
          }),
        ),
      );

      const [person] = personRequests();
      const [contact] = contactPointRequests();

      person.flush({ stableTargetId: id("person1") });

      expect(activityRequests()).toHaveLength(0);
      expect(contact.cancelled).toBe(false);

      contact.flush({ stableTargetId: id("contact1") });

      const [activity] = activityRequests();
      expect(activity).toBeDefined();

      activity.flush({ $type: "ActivityRuleSetResponse" });
      await done;
    });

    it("does not send the activity when creating a new item fails", async () => {
      const { state, done } = track(
        service.submit(makeActivityModel({ involvedPerson: [createPerson()] })),
      );

      fail(personRequests()[0]);
      await done;

      expect(state.value).toMatchObject({ success: false });
      expect(activityRequests()).toHaveLength(0);

      const error = errorOf(state.value);
      expect(error).toBeInstanceOf(SubmissionError);
      expect(error.innerError).toBeInstanceOf(HttpErrorResponse);
    });

    it("cancels outstanding reference requests when one fails", async () => {
      const { state, done } = track(
        service.submit(
          makeActivityModel({
            contact: [createContactPoint()],
            involvedPerson: [createPerson("Alice", "One"), createPerson("Bob", "Two")],
          }),
        ),
      );

      const persons = personRequests();
      const [contact] = contactPointRequests();
      expect(persons).toHaveLength(2);

      fail(contact);
      await done;

      expect(state.value).toMatchObject({ success: false });
      expect(persons.every((request) => request.cancelled)).toBe(true);
      expect(activityRequests()).toHaveLength(0);
    });

    it("treats a response without stableTargetId as a failure", async () => {
      const { state, done } = track(
        service.submit(makeActivityModel({ involvedPerson: [createPerson()] })),
      );

      personRequests()[0].flush({});
      await done;

      expect(state.status).toBe("resolved");
      expect(state.value).toMatchObject({ success: false });
      expect(errorOf(state.value).innerError?.message).toBe("No stableTargetId in response.");
      expect(activityRequests()).toHaveLength(0);
    });

    it("treats an empty response body as a failure", async () => {
      const { state, done } = track(
        service.submit(makeActivityModel({ contact: [createContactPoint()] })),
      );

      contactPointRequests()[0].flush(null);
      await done;

      expect(state.value).toMatchObject({ success: false });
      expect(activityRequests()).toHaveLength(0);
    });
  });

  describe("submit: the activity request itself fails", () => {
    it("resolves with success:false and a SubmissionError holding the payload and HTTP error", async () => {
      const { state, done } = track(service.submit(makeActivityModel()));

      const [request] = activityRequests();
      fail(request);
      await done;

      expect(state.status).toBe("resolved");
      const error = errorOf(state.value);

      expect(error).toBeInstanceOf(SubmissionError);
      expect(error.message).toBe("Error while submitting 'ActivityRuleSetRequest'");
      expect(error.payload).toEqual(bodyOf(request));
      expect(error.innerError).toBeInstanceOf(HttpErrorResponse);
      expect(error.innerError).toMatchObject({ status: 500 });
    });

    it("reports network errors with status 0", async () => {
      const { state, done } = track(service.submit(makeActivityModel()));

      activityRequests()[0].error(new ProgressEvent("error"));
      await done;

      expect(state.status).toBe("resolved");
      expect(errorOf(state.value).innerError).toMatchObject({
        status: 0,
      });
    });

    it("remains usable after a failed submission", async () => {
      const failing = track(service.submit(makeActivityModel()));

      fail(activityRequests()[0]);
      await failing.done;

      expect(failing.state.value).toMatchObject({ success: false });

      const retry = track(service.submit(makeActivityModel()));

      activityRequests()[0].flush({
        $type: "ActivityRuleSetResponse",
      });
      await retry.done;

      expect(retry.state.value).toMatchObject({ success: true });
    });
  });
});
