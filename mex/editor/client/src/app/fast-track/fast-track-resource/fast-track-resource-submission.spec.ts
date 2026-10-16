import { TestBed } from "@angular/core/testing";

import { FastTrackResourceSubmission } from "./fast-track-resource-submission";

describe("ResourceSubmission", () => {
  let service: FastTrackResourceSubmission;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FastTrackResourceSubmission);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
