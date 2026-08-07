import { TestBed } from "@angular/core/testing";

import { ConceptOptions } from "../../shared/concept-options.service";

describe("ConceptOptions", () => {
  let service: ConceptOptions;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConceptOptions);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
