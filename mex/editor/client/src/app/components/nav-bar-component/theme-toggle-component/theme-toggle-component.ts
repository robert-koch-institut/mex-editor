import type { OnInit } from "@angular/core";
import { Renderer2 } from "@angular/core";
import { Component, DOCUMENT, inject, signal } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { TranslocoPipe } from "@jsverse/transloco";

/**
 * Component to toggle the current theme between dark and light mode.
 */
@Component({
  selector: "app-theme-toggle-component",
  imports: [MatButtonModule, MatIconModule, TranslocoPipe],
  templateUrl: "./theme-toggle-component.html",
  styleUrl: "./theme-toggle-component.scss",
})
export class ThemeToggleComponent implements OnInit {
  private _renderer = inject(Renderer2);
  private _document: Document = inject(DOCUMENT);

  isDarkMode = signal<boolean>(
    !!window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches,
  );

  ngOnInit(): void {
    this._applyMode();
  }

  private _applyMode() {
    if (this.isDarkMode()) {
      this._renderer.addClass(this._document.documentElement, "dark-mode");
    } else {
      this._renderer.removeClass(this._document.documentElement, "dark-mode");
    }
  }

  toggleTheme() {
    // Flip the signal's boolean value
    this.isDarkMode.update((dark) => !dark);
    this._applyMode();
  }
}
