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

import type { Link } from "../../shared/models/generated/shared";
import { LinkSchema } from "../../shared/models/generated/shared";

const emptyToNull = (v: string): string | null | undefined => (v === "" ? null : v);
/**
 * LinkDraftSchema API documentation.
 */
export const LinkDraftSchema = z.object({
  language: z.string().transform(emptyToNull).pipe(LinkSchema.shape.language),
  title: z.string().transform(emptyToNull).pipe(LinkSchema.shape.title),
  url: LinkSchema.shape.url,
});
/**
 * LinkDraft API documentation.
 */
export interface LinkDraft {
  language: string;
  title: string;
  url: string;
}
/**
 * toDraft API documentation.
 */
export function toDraft(link: Link | null | undefined): LinkDraft {
  return {
    language: (link?.language as string | null | undefined) ?? "",
    title: link?.title ?? "",
    url: link?.url ?? "",
  };
}

/**
 * fromDraft API documentation.
 */
export function fromDraft(d: LinkDraft): Link {
  return {
    language: d.language === "" ? null : (d.language as Link["language"]),
    title: d.title === "" ? null : d.title,
    url: d.url,
  };
}

/**
 * sameDraft API documentation.
 */
export function sameDraft(a: LinkDraft, b: LinkDraft): boolean {
  return a.language === b.language && a.title === b.title && a.url === b.url;
}

/** Treats '', null and undefined as equal for optional fields. */
export function sameLink(a: Link, b: Link): boolean {
  const opt = (v: unknown) => (v === "" || v === undefined ? null : v);
  return opt(a.language) === opt(b.language) && opt(a.title) === opt(b.title) && a.url === b.url;
}

@Component({
  selector: "mex-link-editor",
  imports: [FormField, MatFormFieldModule, MatIconModule, MatInput, TranslocoDirective],
  templateUrl: "./link-editor.html",
  styleUrl: "./link-editor.scss",
})
/**
 * Component to edit link objects.
 */
export class LinkEditor implements FormValueControl<Link> {
  // --- Contract ---
  readonly value = model<Link>({ url: "" });

  // --- Configuration ---
  /** Options for the language select. value = what the schema expects. */
  readonly languageOptions = [
    { value: "de", label: "Deutsch" },
    { value: "en", label: "English" },
  ];

  // --- Optional form state (filled by [formField]) ---
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly hidden = input(false);
  readonly invalid = input(false);
  readonly errors = input<readonly WithOptionalFieldTree<ValidationError>[]>([]);
  readonly touch = output<void>();

  /** Internal model. Follows external value changes; local edits stay local until pushed back. */
  private readonly draft = linkedSignal<Link, LinkDraft>({
    source: () => this.value(),
    computation: (link) => toDraft(link),
    equal: sameDraft,
  });

  protected readonly linkForm = form(this.draft, (s) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    validateStandardSchema(s as any, LinkDraftSchema as any);
    for (const path of [s.language, s.title, s.url]) {
      disabled(path, { when: () => this.disabled() });
      readonly(path, { when: () => this.readonly() });
    }
  });

  constructor() {
    // draft -> value (only when the content actually differs)
    effect(() => {
      const next = fromDraft(this.draft());
      if (!sameLink(next, untracked(this.value))) {
        this.value.set(next);
      }
    });
  }
}
