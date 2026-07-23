import { TestBed } from "@angular/core/testing";

import { ConceptOptions } from "./concept-options.service";

describe("VocabularySearchService", () => {
  let service: ConceptOptions;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConceptOptions);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
