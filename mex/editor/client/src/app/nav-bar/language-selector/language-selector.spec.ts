import type { HarnessLoader } from "@angular/cdk/testing";
import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { MatButtonToggleGroupHarness } from "@angular/material/button-toggle/testing";
import { TranslocoService } from "@jsverse/transloco";

import { translocoConfig } from "../../transloco";
import { LanguageSelector } from "./language-selector";

describe("LanguageSelectorComponent", () => {
  let component: LanguageSelector;
  let fixture: ComponentFixture<LanguageSelector>;
  let loader: HarnessLoader;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LanguageSelector],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelector);
    component = fixture.componentInstance;
    await fixture.whenStable();

    loader = TestbedHarnessEnvironment.loader(fixture);
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should always render all available languages", async () => {
    const group = await loader.getHarness(MatButtonToggleGroupHarness);

    const allToggles = await group.getToggles();
    expect(translocoConfig.availableLangs.length).toBe(allToggles.length);

    for (const lang of translocoConfig.availableLangs) {
      const toggles = await group.getToggles({ text: lang.label });
      expect(toggles.length).toBe(1);
    }
  });

  it("should always check/highlight the active language", async () => {
    const group = await loader.getHarness(MatButtonToggleGroupHarness);

    const expectActiveLangToBeSelected = async () => {
      const currentLanguage = component.transloco.getActiveLang();
      const langEntry = translocoConfig.availableLangs.find((x) => x.id === currentLanguage);
      assert(langEntry);

      const checkedToggles = await group.getToggles({ checked: true });
      expect(checkedToggles.length).toBe(1);
      expect(await checkedToggles[0].getText()).toBe(langEntry.label);
    };

    await expectActiveLangToBeSelected();

    const transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("en");
    fixture.detectChanges();

    await expectActiveLangToBeSelected();
  });
});
