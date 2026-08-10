import { Component, inject, signal } from "@angular/core";
import { disabled, form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatFormField, MatInput } from "@angular/material/input";
import { MatSelect, MatOption, MatPrefix, MatSuffix } from "@angular/material/select";
import { ConceptLookups } from "../../shared/concept-lookups.service";
import { MatButton } from "@angular/material/button";
import type { FastTrackResourceModel } from "./fast-track-resource.models";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { TranslocoDirective, TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import { Fieldset } from "../fieldset/fieldset";
import { MatIcon } from "@angular/material/icon";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { MatSlideToggle } from "@angular/material/slide-toggle";
import { MatChipsModule } from "@angular/material/chips";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { ReferenceSelect } from "../reference-select/reference-select";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
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
    ReferenceSelect,
  ],
  templateUrl: "./fast-track-resource.html",
  styleUrl: "./fast-track-resource.scss",
})
/**
 * Page to create a resource the fast way.
 */
export class FastTrackResource {
  private translocoService = inject(TranslocoService);
  protected conceptOptions = inject(ConceptLookups);
  protected dateFormats = inject(MAT_DATE_FORMATS);

  constructor() {
    // rewrite dates to refresh ui and render dates based on localization.
    this.translocoService.langChanges$.pipe(takeUntilDestroyed()).subscribe(() =>
      this.model.update((x) => ({
        ...x,
        start: x.start ? x.start.plus(0) : null,
        end: x.end ? x.end.plus(0) : null,
      })),
    );
  }

  isPrefillChecked = signal(false);
  model = signal<FastTrackResourceModel>({
    title: "",
    description: "",
    theme: [],
    resourceTypeGeneral: [],
    spatial: "",
    resourceCreationMethod: [],
    accrualPeriodicity: "",
    start: null,
    end: null,
    hasLegalBasis: "",
    provenance: "",
    rights: "",
    keywords: {
      de: [],
      en: [],
    },
    unitInCharge: [],
    contacts: [],
    creator: [],
    contributingUnit: [],
    contributor: [],
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    minLength(schema.theme, 1, { message: "At least one theme is required" });
    required(schema.unitInCharge, { message: "Need a unit in charge" });
    required(schema.resourceCreationMethod, { message: "Method is required!" });
    minLength(schema.resourceCreationMethod, 1, { message: "At least one is required!" });

    disabled(schema.rights, { when: this.isPrefillChecked });
  });

  prefillRights(fill: boolean) {
    this.model.update((x) => {
      const text = fill
        ? this.translocoService.translate("fasttrack.resource.fields.rights.prefill.text")
        : "";
      return { ...x, rights: text };
    });
  }

  addKeyword(lang: keyof FastTrackResourceModel["keywords"], keyword: string) {
    this.model.update((x) => {
      const unique = new Set([...x.keywords[lang], keyword]);
      return {
        ...x,
        keywords: {
          ...x.keywords,
          [lang]: [...unique.values()],
        },
      };
    });
  }

  removeKeyword(lang: keyof FastTrackResourceModel["keywords"], keyword: string) {
    this.model.update((x) => {
      const unique = new Set(x.keywords[lang]);
      unique.delete(keyword);
      return {
        ...x,
        keywords: { ...x.keywords, [lang]: [...unique.values()] },
      };
    });
  }

  onSubmit() {
    // eslint-disable-next-line no-console
    console.log("FastTrackResource::onSubmit", this.resourceForm(), this.model());
  }
}
