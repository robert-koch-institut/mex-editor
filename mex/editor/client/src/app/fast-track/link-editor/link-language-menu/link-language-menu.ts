import { Component, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { TranslocoPipe } from "@jsverse/transloco";

import { type LinkLanguage, LinkLanguageSchema } from "../../../shared/models/generated/shared";

@Component({
  selector: "mex-link-language-menu",
  imports: [MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger, TranslocoPipe],
  templateUrl: "./link-language-menu.html",
  styleUrl: "./link-language-menu.scss",
})
/**
 * Component to select a link language with a drop down menu.
 */
export class LinkLanguageMenu {
  readonly language = input.required<LinkLanguage>();
  readonly languageSelected = output<LinkLanguage>();

  readonly options = Object.values(LinkLanguageSchema.def.entries);
  readonly disabled = input<boolean>(false);
}
