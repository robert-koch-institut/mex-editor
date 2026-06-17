import { provideHttpClient } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";
import { App } from "./app";
import { getTranslocoTestingModule, translocoConfig } from "./transloco";
import { TranslocoService } from "@jsverse/transloco";
import { Location } from "@angular/common";
import { RouterTestingHarness } from "@angular/router/testing";

describe("App", () => {
  let app: App;
  let fixture: ComponentFixture<App>;
  // let location: Location;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App, getTranslocoTestingModule()],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(App);
    app = fixture.componentInstance;
    await fixture.whenStable();
  });

  function getUrlLanguage(): string | null {
    const location = TestBed.inject(Location);
    const urlParams = new URLSearchParams(location.path());
    return urlParams.get("language");
  }

  it("should create the app", () => {
    expect(app).toBeTruthy();
  });

  it("should update language query param in current url", () => {
    const transloco = TestBed.inject(TranslocoService);

    for (const lang of translocoConfig.availableLangs) {
      transloco.setActiveLang(lang.id);
      fixture.detectChanges()
      expect(getUrlLanguage()).toBe(lang.id);
    }
  });

  it("should add default language to url query params", () => {
    expect(getUrlLanguage()).toBe(translocoConfig.defaultLang);
  });

  it("should change the app language when i navigate with ?language=<lang>", async () => {
    const harness = await RouterTestingHarness.create();

    for (const lang of translocoConfig.availableLangs) {
      // Navigate to a URL containing query parameters
      await harness.navigateByUrl(`/?language=${lang.id}`);
      harness.fixture.detectChanges();
      await harness.fixture.whenStable();
      await fixture.whenStable()

      const transloco = TestBed.inject(TranslocoService);
      expect(transloco.getActiveLang()).toBe(lang.id)
    }
  });
});
