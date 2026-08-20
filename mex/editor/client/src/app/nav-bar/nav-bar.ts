import { Component } from "@angular/core";
import { MatSelectModule } from "@angular/material/select";
import { MatToolbar } from "@angular/material/toolbar";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { MatIcon } from "@angular/material/icon";
import { TranslocoDirective } from "@jsverse/transloco";

import { LanguageSelector } from "./language-selector/language-selector";
import { ThemeToggle } from "./theme-toggle/theme-toggle";

@Component({
  selector: "mex-nav-bar",
  imports: [
    LanguageSelector,
    MatIcon,
    MatSelectModule,
    MatToolbar,
    RouterLink,
    RouterLinkActive,
    ThemeToggle,
    TranslocoDirective,
  ],
  templateUrl: "./nav-bar.html",
  styleUrl: "./nav-bar.scss",
})
/**
 * Component to render the nav-bar for the app.
 */
export class NavBar {}
