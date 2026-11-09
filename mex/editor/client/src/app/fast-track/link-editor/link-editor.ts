/* eslint-disable @typescript-eslint/naming-convention */

import { Component, effect, input, linkedSignal, model, output, untracked } from "@angular/core";
import {
  disabled,
  form,
  FormField,
  type FormValueControl,
  readonly,
  validateStandardSchema,
  type ValidationError,
  type WithOptionalFieldTree,
} from "@angular/forms/signals";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { TranslocoDirective } from "@jsverse/transloco";
import z from "zod";

import { FieldError } from "../../shared/field-error/field-error";
import { asLinkLanguage } from "../../shared/models";
import type { Link, LinkLanguage } from "../../shared/models/generated/shared";
import { LinkSchema } from "../../shared/models/generated/shared";
import { LinkLanguageMenu } from "./link-language-menu/link-language-menu";

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

const LinkDraftSchema = z.object({
  language: draftField(LinkSchema.shape.language),
  title: draftField(LinkSchema.shape.title),
  url: LinkSchema.shape.url,
});

type LinkDraft = z.infer<typeof LinkDraftSchema>;

/**
 * Converts a link to a draft link to be used in the form. Empty strings are used for null and undefined values.
 * @param link The link to convert.
 * @returns The draft link.
 */
export function toDraft(link: Link | null | undefined): LinkDraft {
  return {
    language: (link?.language as LinkLanguage | null | undefined) ?? "",
    title: link?.title ?? "",
    url: link?.url ?? "",
  };
}

/**
 * Checks if a draft is empty. A draft is considered empty if all its fields are empty strings.
 * @param d The draft to check.
 * @returns Returns true if the draft is empty; otherwise false.
 */
export function isEmptyDraft(d: LinkDraft): boolean {
  return d.language === "" && d.title === "" && d.url === "";
}

/**
 * Converts a draft link back to a link. Empty strings are converted to null values. If the draft is empty and nullable is true, null is returned.
 * @param d The draft to convert.
 * @param nullable Define is null is allowed.
 * @returns Returns the link or null if the draft is empty and nullable is true.
 */
export function fromDraft(d: LinkDraft, nullable: boolean): Link | null {
  if (nullable && isEmptyDraft(d)) {
    return null;
  }
  return {
    language: d.language === "" ? null : (d.language as Link["language"]),
    title: d.title === "" ? null : d.title,
    url: d.url,
  };
}

/**
 * Checks if both drafts are the same (comparing their values).
 * @param a The first draft to compare.
 * @param b The second draft to compare.
 * @returns Returns true if both drafts are the same; otherwise false.
 */
export function sameDraft(a: LinkDraft, b: LinkDraft): boolean {
  return a.language === b.language && a.title === b.title && a.url === b.url;
}

@Component({
  selector: "mex-link-editor",
  imports: [
    FieldError,
    FormField,
    LinkLanguageMenu,
    MatFormFieldModule,
    MatIconModule,
    MatInput,
    TranslocoDirective,
  ],
  templateUrl: "./link-editor.html",
  styleUrl: "./link-editor.scss",
})
/**
 * Component to edit link objects.
 */
export class LinkEditor implements FormValueControl<Link | null> {
  readonly value = model<Link | null>({ url: "" });

  readonly nullable = input(false);
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly hidden = input(false);
  readonly invalid = input(false);
  readonly errors = input<readonly WithOptionalFieldTree<ValidationError>[]>([]);
  readonly touch = output<void>();

  readonly touched = input(false);

  readonly asLinkLanguage = asLinkLanguage;

  private readonly draft = linkedSignal<Link | null, LinkDraft>({
    source: () => this.value(),
    computation: (link) => toDraft(link),
    equal: sameDraft,
  });

  protected readonly linkForm = form(this.draft, (s) => {
    validateStandardSchema(s, LinkDraftSchema);
    for (const path of [s.language, s.title, s.url]) {
      disabled(path, { when: () => this.disabled() });
      readonly(path, { when: () => this.readonly() });
    }
  });

  constructor() {
    effect(() => {
      const touched = this.touched();
      untracked(() => (touched ? this.linkForm().markAsTouched() : this.linkForm().reset()));
    });

    effect(() => {
      const draft = this.draft();
      const current = untracked(this.value);
      // null, undefined and an empty link all look the same in the draft: nothing to write.
      if (sameDraft(draft, toDraft(current))) {
        return;
      }
      this.value.set(fromDraft(draft, untracked(this.nullable)));
    });
  }
}
