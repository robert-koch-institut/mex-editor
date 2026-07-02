import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { NavBarComponent } from "./nav-bar-component";
import { provideRouter } from "@angular/router";
import { routes } from "../../app.routes";
import { RouterTestingHarness } from "@angular/router/testing";
import { CreatePage } from "../../pages/create-page/create-page";
import { StartPage } from "../../pages/start-page/start-page";

describe("NavBarComponent", () => {
  let component: NavBarComponent;
  let fixture: ComponentFixture<NavBarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavBarComponent],
      providers: [provideRouter(routes)],
    }).compileComponents();

    fixture = TestBed.createComponent(NavBarComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should add active class to links", async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl("/create/resource", CreatePage);
    let activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(1);

    await harness.navigateByUrl("/create/activity", CreatePage);
    activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(1);

    await harness.navigateByUrl("/", StartPage);
    activeLinks = fixture.nativeElement.querySelectorAll(".link.active");
    expect(activeLinks.length).toBe(0);
  });
});
