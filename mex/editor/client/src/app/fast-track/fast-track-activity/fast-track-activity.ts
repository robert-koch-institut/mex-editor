import { Component, signal } from "@angular/core";
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
import { TranslocoDirective, TranslocoPipe } from "@jsverse/transloco";

import { FieldCategoryPipe } from "../../shared/field-category-pipe";
import { Datepicker } from "../datepicker/datepicker";
import { Fieldset } from "../fieldset/fieldset";
import { ReferenceSelect } from "../reference-select/reference-select";
import type { FastTrackActivityModel } from "./fast-track-activity.model";
import { FastTrackActivityModelSchema } from "./fast-track-activity.model";

@Component({
  selector: "mex-fast-track-activity",
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
  protected readonly activitySchema = FastTrackActivityModelSchema;

  model = signal<FastTrackActivityModel>({});

  activityForm = form(
    this.model,
    (schema) => {
      validateStandardSchema(schema, FastTrackActivityModelSchema);
    },
    {
      submission: {
        action: async (field) => {
          const validModel = field().value();
          console.log("SUBMITTED", validModel);
        },
        onInvalid: (field) => {
          const firstError = field().errorSummary()[0];
          firstError?.fieldTree().focusBoundControl();
        },
      },
    },
  );
}
