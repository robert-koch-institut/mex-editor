import { Component, signal } from "@angular/core";
import { MatSelectModule } from "@angular/material/select";

@Component({
  selector: "mex-language-selector",
  imports: [MatSelectModule],
  templateUrl: "./language-selector.html",
  styleUrl: "./language-selector.scss",
})
export class LanguageSelector {
  currentLanguage = signal("de");

  changeLanguage(language: string) {
    this.currentLanguage.set(language);
    // eslint-disable-next-line no-console
    console.log("Language changed to:", language);
  }
}
