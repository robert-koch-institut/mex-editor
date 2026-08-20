import { Component } from "@angular/core";
import { MatToolbar } from "@angular/material/toolbar";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { MatSelectModule } from "@angular/material/select";
import { MatIcon } from "@angular/material/icon";
import { LanguageSelector } from "./language-selector/language-selector";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "mex-nav-bar",
  imports: [
    MatToolbar,
    LanguageSelector,
    RouterLink,
    RouterLinkActive,
    MatSelectModule,
    MatIcon,
    TranslocoDirective,
  ],
  templateUrl: "./nav-bar.html",
  styleUrl: "./nav-bar.scss",
})
/**
 * Component to render the nav-bar for the app.
 */
export class NavBar {}
