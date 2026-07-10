import { AsyncPipe } from "@angular/common";
import { Component, inject } from "@angular/core";
import { MatSelectModule } from "@angular/material/select";
import type { LangDefinition } from "@jsverse/transloco";
import { TranslocoService } from "@jsverse/transloco";

/**
 * Component to switch the current active language.
 */
@Component({
  selector: "app-language-selector-component",
  imports: [MatSelectModule, AsyncPipe],
  templateUrl: "./language-selector-component.html",
  styleUrl: "./language-selector-component.scss",
})
export class LanguageSelectorComponent {
  transloco = inject(TranslocoService);
  get currentLanguage$() {
    return this.transloco.langChanges$;
  }
  get availableLanguages() {
    return this.transloco.getAvailableLangs() as LangDefinition[];
  }

  changeLanguage(language: string) {
    this.transloco.setActiveLang(language);
  }
}
