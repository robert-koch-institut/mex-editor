import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { NavBar } from "./nav-bar";
import { provideRouter } from "@angular/router";
import { routes } from "../app.routes";
import { RouterTestingHarness } from "@angular/router/testing";
import { provideHttpClient, withXhr } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import { StartPage } from "../start-page/start-page";
import { FastTrackResource } from "../fast-track-resource/fast-track-resource";
import { FastTrackActivity } from "../fast-track-activity/fast-track-activity";

describe("NavBarComponent", () => {
  let component: NavBar;
  let fixture: ComponentFixture<NavBar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavBar],
      providers: [provideRouter(routes), provideHttpClient(withXhr()), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(NavBar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should add active class to links", async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl("/create/resource", FastTrackResource);
    let activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(1);

    await harness.navigateByUrl("/create/activity", FastTrackActivity);
    activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(1);

    await harness.navigateByUrl("/", StartPage);
    activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(0);
  });
});
