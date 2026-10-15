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
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIcon } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatProgressSpinner } from "@angular/material/progress-spinner";
import { MatOption, MatPrefix, MatSelect } from "@angular/material/select";
import { MatSlideToggle } from "@angular/material/slide-toggle";
import { Router } from "@angular/router";
import { TranslocoDirective, TranslocoPipe, TranslocoService } from "@jsverse/transloco";
import type { DateTime } from "luxon";

import { ConceptLookups } from "../../shared/concept-lookups.service";
import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import type { Frequency } from "../../shared/models/generated/resource";
import { ToastNotifier } from "../../shared/toasts/toast-notifier";
import { Datepicker } from "../datepicker/datepicker";
import { Fieldset } from "../fieldset/fieldset";
import { ReferenceSelect } from "../reference-select/reference-select";
import {
  type FastTrackResourceModel,
  FastTrackResourceModelSchema,
} from "./fast-track-resource.models";
import { FastTrackResourceSubmission } from "./fast-track-resource-submission";

@Component({
  selector: "mex-fast-track-resource",
  imports: [
    Datepicker,
    FieldCategoryPipe,
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
    MatProgressSpinner,
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
  private readonly translocoService = inject(TranslocoService);

  private readonly router = inject(Router);
  private readonly notifier = inject(ToastNotifier);
  protected readonly resourceSchema = FastTrackResourceModelSchema;
  protected readonly conceptOptions = inject(ConceptLookups);
  protected readonly submission = inject(FastTrackResourceSubmission);

  isPrefillChecked = signal(false);
  model = signal<FastTrackResourceModel>({
    title: "",
    description: "",
    theme: [],
    resourceTypeGeneral: [],
    spatial: "",
    resourceCreationMethod: [],
    accrualPeriodicity: null as unknown as Frequency,
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

  resourceForm = form(
    this.model,
    (schema) => {
      validateStandardSchema(schema, FastTrackResourceModelSchema);
      disabled(schema.rights, { when: this.isPrefillChecked });
    },
    {
      submission: {
        action: async (field) => {
          const validModel = field().value();
          const submitResult = await this.submission.submit(validModel);
          if (submitResult.success) {
            this.router.navigate(["edit", submitResult.response.stableTargetId]);
            this.notifier.success(
              this.translocoService.translate("fasttrack.resource.toast.success.message"),
              this.translocoService.translate("fasttrack.resource.toast.success.title"),
            );
          } else {
            this.notifier.submissionFailure(
              this.translocoService.translate("fasttrack.resource.toast.submissionFailure.message"),
              this.translocoService.translate("fasttrack.resource.toast.submissionFailure.title"),
              submitResult,
            );
          }
        },
        onInvalid: (field) => {
          const firstError = field().errorSummary()[0];
          firstError?.fieldTree().focusBoundControl();
        },
      },
    },
  );

  prefillRights(fill: boolean) {
    this.model.update((x) => {
      const text = fill
        ? this.translocoService.translate("fasttrack.resource.fields.rights.prefill.text")
        : "";
      return { ...x, rights: text };
    });
  }

  addKeyword(lang: keyof FastTrackResourceModel["keywords"], keyword: string) {
    keyword = keyword.trim();
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
}
