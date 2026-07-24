import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackResource } from "./fast-track-resource";

describe("FastTrackResource", () => {
  let component: FastTrackResource;
  let fixture: ComponentFixture<FastTrackResource>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackResource],
      providers: [],
    }).compileComponents();

    fixture = TestBed.createComponent(FastTrackResource);
    component = fixture.componentInstance;

    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
