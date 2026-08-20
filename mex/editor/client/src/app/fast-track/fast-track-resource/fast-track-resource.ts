import { Component, inject, signal } from "@angular/core";
import {
  disabled,
  form,
  FormField,
  FormRoot,
  validateStandardSchema,
} from "@angular/forms/signals";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { MatButton } from "@angular/material/button";
import { MatChipsModule } from "@angular/material/chips";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIcon } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatOption, MatPrefix, MatSelect } from "@angular/material/select";
import { MatSlideToggle } from "@angular/material/slide-toggle";
import { TranslocoDirective, TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { DateTime } from "luxon";

import { ConceptLookups } from "../../shared/concept-lookups.service";
import { Datepicker } from "../datepicker/datepicker";
import { Fieldset } from "../fieldset/fieldset";
import { ReferenceSelect } from "../reference-select/reference-select";
import {
  type FastTrackResourceModel,
  FastTrackResourceModelSchema,
} from "./fast-track-resource.models";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    Datepicker,
    Fieldset,
    FormField,
    FormRoot,
    MatAutocompleteModule,
    MatButton,
    MatChipsModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatIcon,
    MatInput,
    MatOption,
    MatPrefix,
    MatSelect,
    MatSlideToggle,
    ReferenceSelect,
    TranslocoDirective,
    TranslocoPipe,
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

  isPrefillChecked = signal(false);
  model = signal<FastTrackResourceModel>({
    title: "",
    description: "",
    theme: [],
    resourceTypeGeneral: [],
    spatial: "",
    resourceCreationMethod: [],
    accrualPeriodicity: null,
    start: null as unknown as DateTime,
    end: null,
    hasLegalBasis: "",
    provenance: "",
    rights: "",
    keywords: {
      de: [],
      en: [],
    },
    unitInCharge: [],
    contact: [],
    creator: [],
    contributingUnit: [],
    contributor: [],
  });

  resourceForm = form(this.model, (schema) => {
    validateStandardSchema(schema, FastTrackResourceModelSchema);
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
    if (keyword) {
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
