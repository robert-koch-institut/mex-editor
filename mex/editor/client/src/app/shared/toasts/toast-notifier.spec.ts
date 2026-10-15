import { TestBed } from "@angular/core/testing";

import { ToastNotifier } from "../toast-notifier";

describe("ToastNotifier", () => {
  let service: ToastNotifier;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ToastNotifier);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
