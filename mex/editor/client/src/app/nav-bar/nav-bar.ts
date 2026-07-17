import { Component } from "@angular/core";
import { MatToolbar } from "@angular/material/toolbar";
import { ThemeToggle } from "./theme-toggle/theme-toggle";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { MatSelectModule } from "@angular/material/select";
import { LanguageSelector } from "./language-selector/language-selector";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "mex-nav-bar",
  imports: [
    MatToolbar,
    LanguageSelector,
    ThemeToggle,
    RouterLink,
    RouterLinkActive,
    MatSelectModule,
    TranslocoDirective,
  ],
  templateUrl: "./nav-bar.html",
  styleUrl: "./nav-bar.scss",
})
/**
 * Component to render the nav-bar for the app.
 */
export class NavBar {}
