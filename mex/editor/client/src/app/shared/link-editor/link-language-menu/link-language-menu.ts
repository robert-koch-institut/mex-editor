import { Component, computed, inject, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { translateSignal } from "@jsverse/transloco";

import { ConceptLookups } from "../../concept-lookups.service";
import { type LinkLanguage } from "../../models/generated/shared";

type MaybeNullabelLinkLanguage<T extends true | false> = T extends true
  ? LinkLanguage | null
  : LinkLanguage;

@Component({
  selector: "mex-link-language-menu",
  imports: [MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger],
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

  private readonly lookups = inject(ConceptLookups);
  private readonly noneLanguageLabel = translateSignal("language.none");

  readonly options = computed(() => [
    ...this.lookups.linkLanguageOptions(),
    ...(this.nullable() ? [{ value: null, label: this.noneLanguageLabel(), data: null }] : []),
  ]);
  readonly disabled = input<boolean>(false);

  onLanguageSelected(value: LinkLanguage | null) {
    this.languageSelected.emit(value as MaybeNullabelLinkLanguage<T>);
  }
}
