import { Component } from "@angular/core";
import { MatToolbar } from "@angular/material/toolbar";
import { ThemeToggleComponent } from "./theme-toggle-component/theme-toggle-component";
import { RouterLink, RouterLinkActive } from "@angular/router";
import { MatSelectModule } from "@angular/material/select";
import { LanguageSelectorComponent } from "./language-selector-component/language-selector-component";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "app-nav-bar-component",
  imports: [
    MatToolbar,
    LanguageSelectorComponent,
    ThemeToggleComponent,
    RouterLink,
    RouterLinkActive,
    MatSelectModule,
    TranslocoDirective
  ],
  templateUrl: "./nav-bar-component.html",
  styleUrl: "./nav-bar-component.scss",
})
export class NavBarComponent {}
