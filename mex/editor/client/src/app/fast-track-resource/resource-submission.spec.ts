import { TestBed } from "@angular/core/testing";

import testProviders from "../../test-providers";
import { ResourceSubmission } from "./resource-submission";

describe("ResourceSubmission", () => {
  let service: ResourceSubmission;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [...testProviders] });
    service = TestBed.inject(ResourceSubmission);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
