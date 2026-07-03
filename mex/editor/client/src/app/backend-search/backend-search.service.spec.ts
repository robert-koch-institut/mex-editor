import { TestBed } from "@angular/core/testing";

import { BackendSearchService } from "./backend-search.service";
import type { PreviewOrganizationalUnit } from "./backend-search.types";

describe("BackendSearchService", () => {
  let service: BackendSearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BackendSearchService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });

  it("maps units to options preferring the German name", () => {
    const units: PreviewOrganizationalUnit[] = [
      {
        identifier: "unit-1",
        name: [
          { value: "Abteilung", language: "de" },
          { value: "Department", language: "en" },
        ],
      },
    ];

    expect(service.toOptions(units)).toEqual([{ id: "unit-1", label: "Abteilung" }]);
  });

  it("falls back to the first name, then the identifier", () => {
    const units: PreviewOrganizationalUnit[] = [
      {
        identifier: "unit-en",
        name: [{ value: "English only", language: "en" }],
      },
      {
        identifier: "unit-none",
        name: [],
      },
    ];

    expect(service.toOptions(units)).toEqual([
      { id: "unit-en", label: "English only" },
      { id: "unit-none", label: "unit-none" },
    ]);
  });
});
