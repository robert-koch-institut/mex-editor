import { TestBed } from "@angular/core/testing";

import { BackendProxyService } from "./backend-proxy-service";

describe("BackendProxy", () => {
  let service: BackendProxyService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BackendProxyService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
