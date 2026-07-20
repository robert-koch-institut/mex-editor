import { provideHttpClient, withXhr } from "@angular/common/http";
import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackResource } from "./fast-track-resource";
import type { PreviewOrganizationalUnit } from "../shared/models";
import type { Concept } from "./vocabulary-search.types";

describe("FastTrackResource", () => {
  let component: FastTrackResource;
  let fixture: ComponentFixture<FastTrackResource>;
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackResource],
      providers: [provideHttpClient(withXhr()), provideHttpClientTesting()],
    }).compileComponents();

    httpTesting = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(FastTrackResource);
    component = fixture.componentInstance;
    // Kick off the vocabulary httpResources and satisfy their pending requests
    // so the fixture can stabilize.
    fixture.detectChanges();
    for (const vocabulary of [
      "theme",
      "resource-creation-method",
      "frequency",
      "access-restriction",
    ]) {
      httpTesting.expectOne(`api/v0/vocabulary/${vocabulary}`).flush({ items: [], total: 0 });
    }
    // The "unit in charge" field fires a backend search on init (empty query).
    for (const request of httpTesting.match((r) =>
      r.url.startsWith("api/v0/backend/preview-item"),
    )) {
      request.flush({ items: [], total: 0 });
    }
    await fixture.whenStable();
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it("maps units to options preferring the German name", () => {
    const units: PreviewOrganizationalUnit[] = [
      {
        $type: "PreviewOrganizationalUnit",
        identifier: "unit-1",
        name: [
          { value: "Abteilung", language: "de" },
          { value: "Department", language: "en" },
        ],
      },
    ];

    expect(FastTrackResource.toOptions(units)).toEqual([{ id: "unit-1", label: "Abteilung" }]);
  });

  it("falls back to the first name, then the identifier", () => {
    const units: PreviewOrganizationalUnit[] = [
      {
        $type: "PreviewOrganizationalUnit",
        identifier: "unit-en",
        name: [{ value: "English only", language: "en" }],
      },
      {
        $type: "PreviewOrganizationalUnit",
        identifier: "unit-none",
        name: [],
      },
    ];

    expect(FastTrackResource.toOptions(units)).toEqual([
      { id: "unit-en", label: "English only" },
      { id: "unit-none", label: "unit-none" },
    ]);
  });

  it("maps concepts to options preferring the German label", () => {
    const concepts: Concept[] = [
      {
        identifier: "https://mex.rki.de/item/resource-type-general-1",
        inScheme: "https://mex.rki.de/item/resource-type-general",
        prefLabel: { de: "Datensatz", en: "Dataset" },
        altLabel: [],
      },
    ];

    expect(FastTrackResource.toOptions(concepts)).toEqual([
      { id: "https://mex.rki.de/item/resource-type-general-1", label: "Datensatz" },
    ]);
  });

  it("falls back to the English label, then the identifier", () => {
    const concepts: Concept[] = [
      {
        identifier: "id-en",
        inScheme: "scheme",
        prefLabel: { de: null, en: "English only" },
        altLabel: [],
      },
      {
        identifier: "id-none",
        inScheme: "scheme",
        prefLabel: {},
        altLabel: [],
      },
    ];

    expect(FastTrackResource.toOptions(concepts)).toEqual([
      { id: "id-en", label: "English only" },
      { id: "id-none", label: "id-none" },
    ]);
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
