import { TestBed } from "@angular/core/testing";

import { ContactSearch } from "./contact-search";

describe("ContactSearch", () => {
  let service: ContactSearch;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ContactSearch);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
