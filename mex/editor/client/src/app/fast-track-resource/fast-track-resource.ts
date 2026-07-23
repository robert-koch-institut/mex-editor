import { Component, computed, inject, Injectable, signal } from "@angular/core";
import { disabled, form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatFormField, MatInput } from "@angular/material/input";
import { MatSelect, MatOption, MatPrefix, MatSuffix } from "@angular/material/select";

import { ConceptOptions } from "./concept-options.service";
import { MatButton } from "@angular/material/button";

import type { FastTrackResourceModel } from "./fast-track-resource.types";

import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { ContactList } from "./contact-list/contact-list";
import { ResourceSubmission } from "./resource-submission";
import {
  translateSignal,
  TranslocoDirective,
  TranslocoPipe,
  TranslocoService,
} from "@jsverse/transloco";
import { Fieldset } from "./fieldset/fieldset";
import { MatIcon } from "@angular/material/icon";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { provideLuxonDateAdapter } from "@angular/material-luxon-adapter";
import type { MatDateFormats } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { MatSlideToggle } from "@angular/material/slide-toggle";
import { MatChipsModule } from "@angular/material/chips";
import { MatFormFieldModule } from "@angular/material/form-field";

@Injectable()
/**
 * DynamicDateFormats API documentation.
 */
export class DynamicLuxonFormats implements MatDateFormats {
  private dateAdapter = inject(TranslocoService);

  // Das Parse-Format (wichtig für manuelle Tastatureingaben des Users)
  get parse() {
    const locale = this.dateAdapter.getActiveLang();
    return {
      dateInput: locale === "de" ? "dd.MM.yyyy" : "MM/dd/yyyy",
    };
  }

  // Das Anzeige-Format im Inputfeld und Kalender-Labels
  get display() {
    const locale = this.dateAdapter.getActiveLang();
    const isDe = locale === "de";
    return {
      dateInput: isDe ? "dd.MM.yyyy" : "MM/dd/yyyy",
      monthYearLabel: isDe ? "MMM yyyy" : "MMM yyyy",
      dateA11yLabel: "LL",
      monthYearA11yLabel: "MMMM yyyy",
    };
  }
}

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    ContactList,
    FormField,
    FormRoot,
    MatAutocompleteModule,
    MatButton,
    MatFormField,
    MatInput,
    MatOption,
    MatSelect,
    TranslocoDirective,
    TranslocoPipe,
    Fieldset,
    MatIcon,
    MatPrefix,
    MatSuffix,
    MatDatepickerModule,
    MatSlideToggle,
    MatChipsModule,
    MatFormFieldModule,
  ],
  providers: [
    provideLuxonDateAdapter(),
    { provide: MAT_DATE_FORMATS, useFactory: () => new DynamicLuxonFormats() },
  ],
  templateUrl: "./fast-track-resource.html",
  styleUrl: "./fast-track-resource.scss",
})
/**
 * Page to create a resource the fast way.
 */
export class FastTrackResource {
  private resourceSubmissionService = inject(ResourceSubmission);
  private translocoService = inject(TranslocoService);
  protected conceptOptions = inject(ConceptOptions);
  protected dateFormtConfig = inject(MAT_DATE_FORMATS);

  constructor() {
    // rewrite dates to refresh ui and render dates based on localization.
    this.translocoService.langChanges$.pipe(takeUntilDestroyed()).subscribe(() =>
      this.model.update((x) => ({
        ...x,
        start: x.start ? new Date(x.start) : null,
        end: x.end ? new Date(x.end) : null,
      })),
    );
  }

  prefillRightsText = translateSignal("fasttrack.resource.fields.rights.prefill.text");
  isRightsPrefilled = computed(() => this.model().rights === this.prefillRightsText());

  model = signal<FastTrackResourceModel>({
    title: "",
    description: "",
    theme: [],
    resourceTypeGeneral: [],
    spatial: [],
    resourceCreationMethod: [],
    accrualPeriodicity: "",
    unitInCharge: [],
    contacts: [""],
    start: null,
    end: null,
    hasLegalBasis: "",
    provenance: "",
    rights: "",
    keywords: {
      de: [],
      en: [],
    },
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    minLength(schema.theme, 1, { message: "At least one theme is required" });
    required(schema.unitInCharge, { message: "Need a unit in charge" });
    required(schema.resourceCreationMethod, { message: "Method is required!" });
    minLength(schema.resourceCreationMethod, 1, { message: "At least one is required!" });

    disabled(schema.rights, { when: () => this.isRightsPrefilled() });
  });

  prefillRights(fill: boolean) {
    this.model.update((x) => {
      const text = fill ? this.prefillRightsText() : "";
      return { ...x, rights: text };
    });
  }

  deleteContact(index: number) {
    this.model.update((m) => {
      return { ...m, contacts: m.contacts.filter((_, i) => i !== index) };
    });
  }

  addContact() {
    this.model.update((m) => {
      return { ...m, contacts: [...m.contacts, ""] };
    });
  }

  addKeyword(lang: keyof FastTrackResourceModel["keywords"], keyword: string) {
    this.model.update((x) => {
      const unique = new Set([...x.keywords[lang], keyword]);
      x.keywords[lang] = [...unique.values()];
      return x;
    });
  }

  removeKeyword(lang: keyof FastTrackResourceModel["keywords"], keyword: string) {
    this.model.update((x) => {
      const unique = new Set(x.keywords[lang]);
      unique.delete(keyword);
      x.keywords[lang] = [...unique.values()];
      return x;
    });
  }

  onSubmit() {
    this.resourceSubmissionService.submit(this.model).subscribe((result) => {
      // eslint-disable-next-line no-console
      console.log("Submitted", this.model(), result.stableTargetId);
    });
  }
}
