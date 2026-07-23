import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackResource } from "./fast-track-resource";

describe("FastTrackResource", () => {
  let component: FastTrackResource;
  let fixture: ComponentFixture<FastTrackResource>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackResource],
    }).compileComponents();

    fixture = TestBed.createComponent(FastTrackResource);
    component = fixture.componentInstance;
    // Kick off the vocabulary httpResources and satisfy their pending requests
    // so the fixture can stabilize.
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
