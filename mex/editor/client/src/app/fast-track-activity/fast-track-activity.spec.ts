import type { ComponentFixture} from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackActivity } from "./fast-track-activity";

describe("FastTrackActivity", () => {
  let component: FastTrackActivity;
  let fixture: ComponentFixture<FastTrackActivity>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackActivity],
    }).compileComponents();

    fixture = TestBed.createComponent(FastTrackActivity);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
