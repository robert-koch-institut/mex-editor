import { provideHttpClient, withXhr } from "@angular/common/http";
import { HttpTestingController, provideHttpClientTesting } from "@angular/common/http/testing";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackResource } from "./fast-track-resource";

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

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
