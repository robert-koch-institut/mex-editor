import { TestBed } from "@angular/core/testing";

import { BackendProxy } from "./backend-proxy.service";

describe("BackendSearchService", () => {
  let service: BackendProxy;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BackendProxy);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
