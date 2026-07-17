import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LanguageSelector } from "./language-selector";
import { TranslocoService } from "@jsverse/transloco";
import { translocoConfig } from "../../transloco";

describe("LanguageSelectorComponent", () => {
  let component: LanguageSelector;
  let fixture: ComponentFixture<LanguageSelector>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LanguageSelector],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelector);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should always render the current language", () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const expectCurrentLanguageLabelRendersCorrectly = () => {
      const currentLanguage = component.transloco.getActiveLang();
      const langEntry = translocoConfig.availableLangs.find((x) => x.id === currentLanguage);
      assert(langEntry);
      expect(compiled.textContent).toContain(langEntry.label);
    };

    expectCurrentLanguageLabelRendersCorrectly();

    const transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("en");
    fixture.detectChanges();

    expectCurrentLanguageLabelRendersCorrectly();
  });
});
