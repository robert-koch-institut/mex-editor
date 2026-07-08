import { provideHttpClient } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { provideRouter } from "@angular/router";
import { App } from "./app";
import { translocoConfig, LANGUAGE_QUERY_PARAM } from "./transloco";
import { TranslocoService } from "@jsverse/transloco";
import { Location } from "@angular/common";
import { RouterTestingHarness } from "@angular/router/testing";

describe("App", () => {
  let component: App;
  let fixture: ComponentFixture<App>;
  let transloco: TranslocoService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    transloco = TestBed.inject(TranslocoService);
    fixture = TestBed.createComponent(App);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  function getUrlLanguage(): string | null {
    const location = TestBed.inject(Location);
    const urlParams = new URLSearchParams(location.path());
    return urlParams.get(LANGUAGE_QUERY_PARAM);
  }

  it("should create the app", () => {
    expect(component).toBeTruthy();
  });

  it("should update url language query param when language changes", async () => {
    for (const lang of translocoConfig.availableLangs) {
      transloco.setActiveLang(lang.id);
      await fixture.whenStable()

      expect(getUrlLanguage()).toBe(lang.id);
    }
  });

  it("should change the app language when i navigate with ?language=<lang>", async () => {
    const harness = await RouterTestingHarness.create();
    for (const lang of translocoConfig.availableLangs) {
      await harness.navigateByUrl(`/?language=${lang.id}`);
      harness.fixture.detectChanges();
      await harness.fixture.whenStable();

      expect(transloco.getActiveLang()).toBe(lang.id)
    }
  });
});
