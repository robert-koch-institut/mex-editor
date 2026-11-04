/* eslint-disable @typescript-eslint/naming-convention */

import {
  Component,
  effect,
  forwardRef,
  input,
  linkedSignal,
  model,
  output,
  untracked,
} from "@angular/core";
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
import { translateSignal, TranslocoDirective, TranslocoPipe } from "@jsverse/transloco";
import z from "zod";

import type { Link, LinkLanguage } from "../../shared/models/generated/shared";
import { LinkSchema } from "../../shared/models/generated/shared";
import { asLinkLanguage } from "../../shared/util";
import { LabeledControl } from "../labeled-control";
import { ValidationErrorMessagePipe } from "../validation-error-label-pipe";
import { LinkLanguageMenu } from "./link-language-menu/link-language-menu";
/** Internes Formularmodell: kein null/undefined, damit native Inputs funktionieren. */
export interface LinkDraft {
  language: string;
  title: string;
  url: string;
}

/**
 * Optionales Draft-Feld: '' bedeutet "nicht gesetzt" (null).
 * Delegiert an das Originalschema; der Output-Typ bleibt `string`.
 */
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

/**
 * LinkDraftSchema API documentation.
 */
export const LinkDraftSchema = z.object({
  language: draftField(LinkSchema.shape.language),
  title: draftField(LinkSchema.shape.title),
  url: LinkSchema.shape.url,
});

/** null, undefined und ein leerer Link ergeben denselben leeren Draft. */
export function toDraft(link: Link | null | undefined): LinkDraft {
  return {
    language: (link?.language as LinkLanguage | null | undefined) ?? "",
    title: link?.title ?? "",
    url: link?.url ?? "",
  };
}

/**
 * isEmptyDraft API documentation.
 */
export function isEmptyDraft(d: LinkDraft): boolean {
  return d.language === "" && d.title === "" && d.url === "";
}

/** Mit `nullable` wird ein komplett leerer Draft zu null statt zu einem leeren Link-Objekt. */
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
 * sameDraft API documentation.
 */
export function sameDraft(a: LinkDraft, b: LinkDraft): boolean {
  return a.language === b.language && a.title === b.title && a.url === b.url;
}

@Component({
  selector: "mex-link-editor",
  imports: [
    FormField,
    LinkLanguageMenu,
    MatFormFieldModule,
    MatIconModule,
    MatInput,
    TranslocoDirective,
    TranslocoPipe,
    ValidationErrorMessagePipe,
  ],
  providers: [{ provide: LabeledControl, useExisting: forwardRef(() => LinkEditor) }],
  templateUrl: "./link-editor.html",
  styleUrl: "./link-editor.scss",
})
/**
 * Component to edit link objects.
 */
export class LinkEditor implements FormValueControl<Link | null>, LabeledControl {
  readonly asLinkLanguage = asLinkLanguage;
  readonly labels = {
    url: translateSignal("link-editor.link.url"),
    title: translateSignal("link-editor.link.title"),
    language: translateSignal("link-editor.link.language"),
  };

  /** null is a valid value (no link). It is shown as an empty editor. */
  readonly value = model<Link | null>({ url: "" });

  /** If true, emptying all three fields sets the value to null instead of an empty link object. */
  readonly nullable = input(false);
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly hidden = input(false);
  readonly invalid = input(false);
  readonly errors = input<readonly WithOptionalFieldTree<ValidationError>[]>([]);
  readonly touch = output<void>();

  readonly touched = input(false);

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
