import { HttpTestingController } from "@angular/common/http/testing";
import { ApplicationRef } from "@angular/core";
import { TestBed } from "@angular/core/testing";
import { TranslocoService } from "@jsverse/transloco";

import { ConceptLookups } from "./concept-lookups.service";
import type { Lookup } from "./to-lookup-pipe";
import { ToastNotifier } from "./toasts/toast-notifier";

describe("ConceptLookups", () => {
  let httpMock: HttpTestingController;
  let transloco: TranslocoService;
  let notifier: { error: ReturnType<typeof vi.fn> };

  const vocabularyNames = [
    "theme",
    "resource-type-general",
    "resource-creation-method",
    "frequency",
    "access-restriction",
  ];

  beforeEach(() => {
    notifier = { error: vi.fn() };
    TestBed.configureTestingModule({
      providers: [ConceptLookups, { provide: ToastNotifier, useValue: notifier }],
    });

    httpMock = TestBed.inject(HttpTestingController);
    transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("de");
    vi.spyOn(transloco, "getDefaultLang").mockReturnValue("de");
  });

  // catches duplicate/unexpected requests that expectOne alone wouldn't
  afterEach(() => httpMock.verify());

  it("requests every vocabulary endpoint exactly once, across multiple injections", () => {
    const a = TestBed.inject(ConceptLookups);
    const b = TestBed.inject(ConceptLookups); // providedIn: 'root' -> same instance
    expect(a).toBe(b);

    TestBed.tick(); // fires the effects behind each httpResource

    for (const name of vocabularyNames) {
      httpMock.expectOne(`api/v0/vocabulary/${name}`); // .flush({ items: [], total: 0 });
    }
  });

  it("relabels options when the active language changes, without re-fetching", async () => {
    const service = TestBed.inject(ConceptLookups);
    TestBed.tick();

    httpMock.expectOne("api/v0/vocabulary/theme").flush({
      items: [
        {
          identifier: "1",
          prefLabel: { de: "Bevölkerung", en: "Population" },
          altLabel: [],
        },
        {
          identifier: "2",
          prefLabel: { de: "Gesundheit", en: "Health" },
          altLabel: [],
        },
      ],
      total: 2,
    });
    for (const name of vocabularyNames.filter((n) => n !== "theme")) {
      httpMock.expectOne(`api/v0/vocabulary/${name}`).flush({ items: [], total: 0 });
    }

    await TestBed.inject(ApplicationRef).whenStable();
    const trimData = (x: Lookup<unknown>) => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { data, ...rest } = x;
      return rest;
    };

    expect(service.themeOptions().map(trimData)).toEqual([
      { id: "1", label: "Bevölkerung" },
      { id: "2", label: "Gesundheit" },
    ]);

    transloco.setActiveLang("en");

    expect(service.themeOptions().map(trimData)).toEqual([
      { id: "2", label: "Health" },
      { id: "1", label: "Population" },
    ]);
  });

  it("shows an error notification when loading a vocabulary fails", async () => {
    const service = TestBed.inject(ConceptLookups);
    TestBed.tick();

    const errorResponse = {
      message: "Server error",
    };

    const request = httpMock.expectOne("api/v0/vocabulary/theme");
    request.flush(errorResponse, {
      status: 500,
      statusText: "Internal Server Error",
    });

    // Complete the other requests so afterEach(httpMock.verify) passes.
    for (const name of vocabularyNames.filter((n) => n !== "theme")) {
      httpMock.expectOne(`api/v0/vocabulary/${name}`).flush({ items: [], total: 0 });
    }

    await TestBed.inject(ApplicationRef).whenStable();

    // Evaluate the computed after the HTTP resource enters its error state.
    expect(service.themeOptions()).toEqual([]);

    expect(notifier.error).toHaveBeenCalledOnce();
    expect(notifier.error).toHaveBeenCalledWith(
      {
        msgKey: "errors.services.concept-lookup.loading.message",
        params: { lookupName: "theme" },
      },
      {
        msgKey: "errors.services.concept-lookup.loading.title",
      },
      expect.anything(),
    );
  });
});
