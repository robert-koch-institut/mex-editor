import { Component, computed, inject, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { translateSignal, TranslocoPipe } from "@jsverse/transloco";

import type { NoneLookup } from "../../concept-lookups.service";
import { ConceptLookups } from "../../concept-lookups.service";
import { type TextLanguage } from "../../models/generated/shared";

type MaybeNullabelTextLanguage<T extends true | false> = T extends true
  ? TextLanguage | null
  : TextLanguage;

@Component({
  selector: "mex-text-language-menu",
  imports: [MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger, TranslocoPipe],
  templateUrl: "./text-language-menu.html",
  styleUrl: "./text-language-menu.scss",
})
/**
 * Component to select a link language with a drop down menu.
 */
export class TextLanguageMenu<T extends true | false = false> {
  readonly language = input.required<MaybeNullabelTextLanguage<T>>();
  readonly nullable = input<T>(false as T);
  readonly languageSelected = output<MaybeNullabelTextLanguage<T>>();

  private readonly lookups = inject(ConceptLookups);
  private readonly noneLanguageLabel = translateSignal("language.none");

  readonly options = computed(() => [
    ...this.lookups.textLanguageOptions(),
    ...(this.nullable()
      ? [{ value: null, label: this.noneLanguageLabel(), data: null } as NoneLookup]
      : []),
  ]);
  readonly disabled = input<boolean>(false);

  onLanguageSelected(value: TextLanguage | null) {
    this.languageSelected.emit(value as MaybeNullabelTextLanguage<T>);
  }
}
