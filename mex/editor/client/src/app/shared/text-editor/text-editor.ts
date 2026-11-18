import { Component, effect, input, linkedSignal, model, output, untracked } from "@angular/core";
import type {
  FormValueControl,
  ValidationError,
  WithOptionalFieldTree,
} from "@angular/forms/signals";
import {
  disabled,
  form,
  FormField,
  readonly,
  validateStandardSchema,
} from "@angular/forms/signals";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { TranslocoDirective } from "@jsverse/transloco";
import z from "zod";

import { FieldError } from "../field-error/field-error";
import { asTextLanguage } from "../models";
import type { Text, TextLanguage } from "../models/generated/shared";
import { TextLanguageSchema, TextSchema } from "../models/generated/shared";
import { TextLanguageMenu } from "./text-language-menu/text-language-menu";

function draftField(inner: z.ZodType) {
  return z.string().superRefine((value, ctx) => {
    const result = inner.safeParse(value === "" ? null : value);
    if (!result.success) {
      for (const issue of result.error.issues) {
        ctx.addIssue({ code: "custom", message: issue.message });
      }
    }
  });
}

// eslint-disable-next-line @typescript-eslint/naming-convention
const TextDraftSchema = z.object({
  language: draftField(TextSchema.shape.language),
  value: TextSchema.shape.value,
});

type TextDraft = z.infer<typeof TextDraftSchema>;

/**
 * Converts a text to a draft text to be used in the form. Empty strings are used for null and undefined values.
 * @param text The text to convert.
 * @returns The draft text.
 */
export function toDraft(text: Text | null | undefined): TextDraft {
  return {
    language: text?.language ?? "",
    value: text?.value ?? "",
  };
}

/**
 * Checks if a draft is empty. A draft is considered empty if all its fields are empty strings.
 * @param d The draft to check.
 * @returns Returns true if the draft is empty; otherwise false.
 */
export function isEmptyDraft(d: TextDraft): boolean {
  return d.language === "" && d.value === "";
}

/**
 * Converts a draft text back to a text. Empty strings are converted to null values. If the draft is empty and nullable is true, null is returned.
 * @param d The draft to convert.
 * @param nullable Define if null is allowed.
 * @returns Returns the text or null if the draft is empty and nullable is true.
 */
export function fromDraft(d: TextDraft, nullable: boolean): Text | null {
  if (nullable && isEmptyDraft(d)) {
    return null;
  }
  return {
    language: d.language === "" ? null : (d.language as TextLanguage),
    value: d.value,
  };
}

/**
 * Checks if both drafts are the same (comparing their values).
 * @param a The first draft to compare.
 * @param b The second draft to compare.
 * @returns Returns true if both drafts are the same; otherwise false.
 */
export function sameDraft(a: TextDraft, b: TextDraft): boolean {
  return a.language === b.language && a.value === b.value;
}

@Component({
  imports: [
    FieldError,
    FormField,
    MatFormFieldModule,
    MatIconModule,
    MatInput,
    TextLanguageMenu,
    TranslocoDirective,
  ],
  selector: "mex-text-editor",
  styleUrl: "./text-editor.scss",
  templateUrl: "./text-editor.html",
})
/**
 * Component to edit text objects.
 */
export class TextEditor implements FormValueControl<Text | null> {
  readonly value = model<Text | null>({ value: "" });

  readonly nullable = input(false);
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly hidden = input(false);
  readonly invalid = input(false);
  readonly errors = input<readonly WithOptionalFieldTree<ValidationError>[]>([]);
  readonly touch = output<void>();

  readonly touched = input(false);

  protected readonly languages = TextLanguageSchema.options;

  private readonly draft = linkedSignal<Text | null, TextDraft>({
    source: () => this.value(),
    computation: (text) => toDraft(text),
    equal: sameDraft,
  });

  protected readonly textForm = form(this.draft, (s) => {
    validateStandardSchema(s, TextDraftSchema);
    for (const path of [s.language, s.value]) {
      disabled(path, { when: () => this.disabled() });
      readonly(path, { when: () => this.readonly() });
    }
  });

  constructor() {
    effect(() => {
      const touched = this.touched();
      untracked(() => {
        if (touched) {
          this.textForm().markAsTouched();
        }
      });
    });

    effect(() => {
      const draft = this.draft();
      const current = untracked(this.value);
      // null, undefined and an empty text all look the same in the draft: nothing to write.
      if (sameDraft(draft, toDraft(current))) {
        return;
      }
      this.value.set(fromDraft(draft, untracked(this.nullable)));
    });
  }

  asTextLanguage(value: string, nullable = true) {
    return value === "" && nullable ? null : asTextLanguage(value);
  }
}
