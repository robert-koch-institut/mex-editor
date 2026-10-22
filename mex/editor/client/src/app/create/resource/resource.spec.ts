import { ComponentFixture, TestBed } from "@angular/core/testing";

import { Resource } from "./resource";

describe("Resource", () => {
  let component: Resource;
  let fixture: ComponentFixture<Resource>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Resource],
    }).compileComponents();

    fixture = TestBed.createComponent(Resource);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
