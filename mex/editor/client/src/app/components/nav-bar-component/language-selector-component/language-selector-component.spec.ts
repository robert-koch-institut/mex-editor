import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LanguageSelectorComponent } from "./language-selector-component";
import { getTranslocoTestingModule, translocoConfig } from "../../../transloco";
import { TranslocoService } from "@jsverse/transloco";

describe("LanguageSelectorComponent", () => {
  let component: LanguageSelectorComponent;
  let fixture: ComponentFixture<LanguageSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LanguageSelectorComponent, getTranslocoTestingModule()],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelectorComponent);
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
    fixture.detectChanges()

    expectCurrentLanguageLabelRendersCorrectly();
  });
});
