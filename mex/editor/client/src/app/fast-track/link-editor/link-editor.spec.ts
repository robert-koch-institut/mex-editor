import { Component, signal } from "@angular/core";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import { disabled, form, FormField } from "@angular/forms/signals";
import { By } from "@angular/platform-browser";
import { TranslocoTestingModule } from "@jsverse/transloco";

import type { Link } from "../../shared/models/generated/shared";
import { LinkLanguageSchema } from "../../shared/models/generated/shared";
import { fromDraft, isEmptyDraft, LinkEditor, sameDraft, toDraft } from "./link-editor";
import { LinkLanguageMenu } from "./link-language-menu/link-language-menu";

describe("draft helpers", () => {
  it("maps null, undefined and missing fields to the same empty draft", () => {
    const empty = { language: "", title: "", url: "" };
    expect(toDraft(null)).toEqual(empty);
    expect(toDraft(undefined)).toEqual(empty);
    expect(toDraft({ url: "" })).toEqual(empty);
  });

  it("detects empty drafts", () => {
    expect(isEmptyDraft({ language: "", title: "", url: "" })).toBe(true);
    expect(isEmptyDraft({ language: "", title: "x", url: "" })).toBe(false);
  });

  it("converts empty strings back to null", () => {
    expect(fromDraft({ language: "", title: "", url: "https://a.de" }, false)).toEqual({
      language: null,
      title: null,
      url: "https://a.de",
    });
  });

  it("returns null for an empty draft only when nullable", () => {
    const empty = { language: "", title: "", url: "" };
    expect(fromDraft(empty, true)).toBeNull();
    expect(fromDraft(empty, false)).toEqual({ language: null, title: null, url: "" });
  });

  it("compares drafts by value", () => {
    const a = { language: "", title: "t", url: "u" };
    expect(sameDraft(a, { ...a })).toBe(true);
    expect(sameDraft(a, { ...a, url: "v" })).toBe(false);
  });
});

@Component({
  imports: [FormField, LinkEditor],
  template: `<mex-link-editor [formField]="f.link" [nullable]="nullable()" />`,
})
class HostComponent {
  readonly model = signal<{ link: Link | null }>({ link: { url: "https://example.org" } });
  readonly nullable = signal(false);
  readonly isDisabled = signal(false);
  readonly f = form(this.model, (p) => disabled(p.link, { when: () => this.isDisabled() }));
}

describe("LinkEditor", () => {
  let fixture: ComponentFixture<HostComponent>;
  let host: HostComponent;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        HostComponent,
        TranslocoTestingModule.forRoot({
          langs: { en: {} },
          translocoConfig: { availableLangs: ["en"], defaultLang: "en" },
        }),
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(HostComponent);
    host = fixture.componentInstance;
    el = fixture.nativeElement;
    await fixture.whenStable();
  });

  const urlInput = () => el.querySelector<HTMLInputElement>("input[type=url]")!;
  const titleInput = () => el.querySelectorAll<HTMLInputElement>("input")[1];
  const type = async (input: HTMLInputElement, text: string) => {
    input.value = text;
    input.dispatchEvent(new Event("input"));
    await fixture.whenStable();
  };

  it("shows the value in the inputs", () => {
    expect(urlInput().value).toBe("https://example.org");
    expect(titleInput().value).toBe("");
  });

  it("writes edits back to the model", async () => {
    await type(titleInput(), "Example");
    expect(host.model().link).toEqual({
      url: "https://example.org",
      title: "Example",
      language: null,
    });
  });

  it("writes the language selected in the menu", async () => {
    const lang = Object.values(LinkLanguageSchema.def.entries)[0];
    fixture.debugElement
      .query(By.directive(LinkLanguageMenu))
      .componentInstance.languageSelected.emit(lang);
    await fixture.whenStable();
    expect(host.model().link?.language).toBe(lang);
  });

  it("sets null when all fields are emptied and nullable", async () => {
    host.nullable.set(true);
    await type(urlInput(), "");
    expect(host.model().link).toBeNull();
  });

  it("keeps an empty link object when all fields are emptied and not nullable", async () => {
    await type(urlInput(), "");
    expect(host.model().link).toEqual({ url: "", title: null, language: null });
  });

  it("updates the inputs when the model changes from outside", async () => {
    host.model.set({ link: { url: "https://other.org", title: "Other" } });
    await fixture.whenStable();
    expect(urlInput().value).toBe("https://other.org");
    expect(titleInput().value).toBe("Other");
  });

  it("disables the inputs when the field is disabled", async () => {
    host.isDisabled.set(true);
    await fixture.whenStable();
    expect(urlInput().disabled).toBe(true);
    expect(titleInput().disabled).toBe(true);
  });
});
