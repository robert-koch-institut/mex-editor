import { TestBed } from "@angular/core/testing";

import { ResourceSubmission } from "./resource-submission";

describe("ResourceSubmission", () => {
  let service: ResourceSubmission;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ResourceSubmission);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
