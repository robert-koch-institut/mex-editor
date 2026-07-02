import { Component } from "@angular/core";
import { MatToolbar } from "@angular/material/toolbar";
import { ThemeToggle } from "./theme-toggle/theme-toggle";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { MatSelectModule } from "@angular/material/select";
import { LanguageSelector } from "./language-selector/language-selector";

@Component({
  selector: "mex-nav-bar",
  imports: [
    MatToolbar,
    LanguageSelector,
    ThemeToggle,
    RouterLink,
    RouterLinkActive,
    MatSelectModule,
  ],
  templateUrl: "./nav-bar.html",
  styleUrl: "./nav-bar.scss",
})
export class NavBar {}
