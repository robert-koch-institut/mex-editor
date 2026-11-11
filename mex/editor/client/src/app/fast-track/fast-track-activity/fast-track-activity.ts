import { Component, inject, signal } from "@angular/core";
import { form, FormField, FormRoot, validateStandardSchema } from "@angular/forms/signals";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { MatButton } from "@angular/material/button";
import { MatChipsModule } from "@angular/material/chips";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIcon } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatProgressSpinner } from "@angular/material/progress-spinner";
import { MatOption, MatPrefix, MatSelect } from "@angular/material/select";
import { Router } from "@angular/router";
import { TranslocoDirective, TranslocoPipe, TranslocoService } from "@jsverse/transloco";

import { ConceptLookups } from "../../shared/concept-lookups.service";
import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import { asLinkLanguage } from "../../shared/models";
import type { Link } from "../../shared/models/generated/shared";
import { SubmissionError } from "../../shared/models/submission-result";
import { ToastNotifier } from "../../shared/toasts/toast-notifier";
import {
  ArrayFormValueControl,
  ArrayItemTemplate,
} from "../array-form-value-control/array-form-value-control";
import { Datepicker } from "../datepicker/datepicker";
import type { FastTrackActivityModel } from "../fast-track-activity.model";
import { FastTrackActivityModelSchema } from "../fast-track-activity.model";
import { FastTrackSubmission } from "../fast-track-submission";
import { Fieldset } from "../fieldset/fieldset";
import { LinkEditor } from "../link-editor/link-editor";
import { ReferenceSelect } from "../reference-select/reference-select";

@Component({
  selector: "mex-fast-track-activity",
  imports: [
    ArrayFormValueControl,
    ArrayItemTemplate,
    Datepicker,
    FieldCategoryPipe,
    Fieldset,
    FormField,
    FormRoot,
    LinkEditor,
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
    ReferenceSelect,
    TranslocoDirective,
    TranslocoPipe,
  ],

  templateUrl: "./fast-track-activity.html",
  styleUrl: "./fast-track-activity.scss",
})
/**
 * Page to create an activity in a fast way.
 */
export class FastTrackActivity {
  private readonly router = inject(Router);
  private readonly notifier = inject(ToastNotifier);
  private readonly transloco = inject(TranslocoService);
  private readonly submission = inject(FastTrackSubmission);
  protected readonly conceptOptions = inject(ConceptLookups);
  protected readonly activitySchema = FastTrackActivityModelSchema;

  model = signal<FastTrackActivityModel>({
    $type: "FastTrackActivityModel",
    title: "",
    shortName: "",
    abstract: "",
    contact: [],
    activityType: [],
    funderOrCommissioner: [],
    involvedPerson: [],
    involvedUnit: [],
    responsibleUnit: [],
    website: [],
    end: null,
    start: null,
  });

  activityForm = form(
    this.model,
    (schema) => {
      validateStandardSchema(schema, FastTrackActivityModelSchema);
    },
    {
      submission: {
        action: async (field) => {
          const validModel = field().value();
          const submitResult = await this.submission.submit(validModel);
          if (submitResult.success) {
            this.router.navigate(["edit", submitResult.response.stableTargetId]);
            this.notifier.success(
              { msgKey: "fasttrack.activity.toast.success.message" },
              { msgKey: "fasttrack.activity.toast.success.title" },
            );
          } else if (submitResult.error instanceof SubmissionError) {
            this.notifier.submissionError(
              { msgKey: "fasttrack.activity.toast.submissionError.message" },
              { msgKey: "fasttrack.activity.toast.submissionError.title" },
              submitResult.error as SubmissionError<{ $type: string }>,
            );
          } else {
            this.notifier.error(
              { msgKey: "fasttrack.activity.toast.error.message" },
              { msgKey: "fasttrack.activity.toast.error.title" },
              submitResult.error,
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

  createNewLink = () =>
    ({ url: "", language: asLinkLanguage(this.transloco.getActiveLang()) }) as Link;
}
