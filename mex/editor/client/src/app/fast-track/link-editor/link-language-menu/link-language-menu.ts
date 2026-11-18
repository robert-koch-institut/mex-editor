import { Component, computed, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { TranslocoPipe } from "@jsverse/transloco";

import { type LinkLanguage, LinkLanguageSchema } from "../../../shared/models/generated/shared";

type MaybeNullabelLinkLanguage<T extends true | false> = T extends true
  ? LinkLanguage | null
  : LinkLanguage;

@Component({
  selector: "mex-link-language-menu",
  imports: [MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger, TranslocoPipe],
  templateUrl: "./link-language-menu.html",
  styleUrl: "./link-language-menu.scss",
})
/**
 * Component to select a link language with a drop down menu.
 */
export class LinkLanguageMenu<T extends true | false = false> {
  readonly language = input.required<MaybeNullabelLinkLanguage<T>>();
  readonly nullable = input<T>(false as T);
  readonly languageSelected = output<MaybeNullabelLinkLanguage<T>>();

  readonly options = computed(() => [
    ...Object.values(LinkLanguageSchema.def.entries).map((x) => ({
      value: x,
      labelKey: `language.${x}`,
    })),
    ...(this.nullable() ? [{ value: null, labelKey: "none" }] : []),
  ]);
  readonly disabled = input<boolean>(false);

  onLanguageSelected(value: LinkLanguage | null) {
    this.languageSelected.emit(value as MaybeNullabelLinkLanguage<T>);
  }
}
