import { Component, computed, input, output } from "@angular/core";
import { MatIconButton } from "@angular/material/button";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { TranslocoPipe } from "@jsverse/transloco";

import { type TextLanguage, TextLanguageSchema } from "../../models/generated/shared";

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

  readonly options = computed(() => [
    ...Object.values(TextLanguageSchema.def.entries).map((x) => ({
      value: x,
      labelKey: `language.${x}`,
    })),
    ...(this.nullable() ? [{ value: null, labelKey: "none" }] : []),
  ]);
  readonly disabled = input<boolean>(false);

  onLanguageSelected(value: TextLanguage | null) {
    this.languageSelected.emit(value as MaybeNullabelTextLanguage<T>);
  }
}
