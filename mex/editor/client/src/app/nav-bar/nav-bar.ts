import { Component } from "@angular/core";
import { MatIcon } from "@angular/material/icon";
import { MatSelectModule } from "@angular/material/select";
import { MatToolbar } from "@angular/material/toolbar";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { TranslocoDirective } from "@jsverse/transloco";

import { LanguageSelector } from "./language-selector/language-selector";

@Component({
  selector: "mex-nav-bar",
  imports: [
    LanguageSelector,
    MatIcon,
    MatSelectModule,
    MatToolbar,
    RouterLink,
    RouterLinkActive,
    TranslocoDirective,
  ],
  templateUrl: "./nav-bar.html",
  styleUrl: "./nav-bar.scss",
})
/**
 * Component to render the nav-bar for the app.
 */
export class NavBar {}
