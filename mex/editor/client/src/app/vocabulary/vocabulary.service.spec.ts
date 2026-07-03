import { TestBed } from "@angular/core/testing";

import { VocabularyService } from "./vocabulary.service";
import type { Concept } from "./vocabulary.types";

describe("VocabularyService", () => {
  let service: VocabularyService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VocabularyService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
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

    expect(service.toOptions(concepts)).toEqual([
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

    expect(service.toOptions(concepts)).toEqual([
      { id: "id-en", label: "English only" },
      { id: "id-none", label: "id-none" },
    ]);
  });
});
