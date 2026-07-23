import { TestBed } from "@angular/core/testing";

import { ConceptOptions } from "./concept-options.service";
import { HttpTestingController } from "@angular/common/http/testing";

describe("ConceptOptions", () => {
  let service: ConceptOptions;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConceptOptions);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
