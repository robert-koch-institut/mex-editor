import { AsyncPipe } from "@angular/common";
import { Component, inject } from "@angular/core";
import { MatSelectModule } from "@angular/material/select";
import type { LangDefinition } from "@jsverse/transloco";
import { TranslocoService } from "@jsverse/transloco";

@Component({
  selector: "mex-language-selector",
  imports: [MatSelectModule, AsyncPipe],
  templateUrl: "./language-selector.html",
  styleUrl: "./language-selector.scss",
})
/**
 * Component to switch the current active language.
 */
export class LanguageSelector {
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
