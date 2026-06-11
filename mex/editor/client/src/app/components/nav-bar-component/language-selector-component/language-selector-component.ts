import { Component, signal } from "@angular/core";
import { MatSelectModule } from "@angular/material/select";

@Component({
  selector: "app-language-selector-component",
  imports: [MatSelectModule],
  templateUrl: "./language-selector-component.html",
  styleUrl: "./language-selector-component.scss",
})
export class LanguageSelectorComponent {
  currentLanguage = signal("de");

  changeLanguage(language: string) {
    this.currentLanguage.set(language);
    // eslint-disable-next-line no-console
    console.log("Language changed to:", language);
  }
}
