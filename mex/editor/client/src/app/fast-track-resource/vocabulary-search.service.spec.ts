import { TestBed } from "@angular/core/testing";

import { VocabularySearch } from "./vocabulary-search.service";

describe("VocabularySearchService", () => {
  let service: VocabularySearch;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VocabularySearch);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
