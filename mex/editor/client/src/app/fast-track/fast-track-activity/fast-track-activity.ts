import { LiveAnnouncer } from "@angular/cdk/a11y";
import { Component, inject, signal } from "@angular/core";
import {
  form,
  FormField,
  FormRoot,
  minDate,
  minLength,
  required,
  validate,
} from "@angular/forms/signals";
import { MatButton } from "@angular/material/button";
import type { MatChipInputEvent } from "@angular/material/chips";
import { MatChipsModule } from "@angular/material/chips";
import { MatNativeDateModule } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatInput } from "@angular/material/input";
import { MatInputModule } from "@angular/material/input";
import { MatError, MatFormField, MatHint, MatLabel } from "@angular/material/select";

/**
 * Model for a contact point that is created inline with the activity.
 */
export interface CreateContactPointModel {
  $type: "CreateContactPointModel";
  email: string;
}
/**
 * Model for a person that is created inline with the activity.
 */
export interface CreatePersonModel {
  $type: "CreatePersonModel";
  firstname: number;
  lastname: number;
}
/**
 * Union of the contact types that can be created inline with the activity.
 */
export type CreateContactModel = CreateContactPointModel | CreatePersonModel;
/**
 * Model backing the fast-track activity form.
 */
export interface FastTrackActivityModel {
  title: string;
  contact: (string | CreateContactModel)[];
  startDate: Date | null;
  endDate: Date | null;
  keywords: KeywordDict;
}
/**
 * Keywords of an activity, grouped by language.
 */
export interface KeywordDict {
  german: string[];
  english: string[];
}

@Component({
  selector: "mex-fast-track-activity",
  imports: [
    FormField,
    FormRoot,
    MatButton,
    MatChipsModule,
    MatDatepickerModule,
    MatDatepickerModule,
    MatError,
    MatFormField,
    MatFormFieldModule,
    MatHint,
    MatIconModule,
    MatInput,
    MatInputModule,
    MatLabel,
    MatNativeDateModule,
    MatNativeDateModule,
  ],

  templateUrl: "./fast-track-activity.html",
  styleUrl: "./fast-track-activity.scss",
})
/**
 * Page to create an activity in a fast way.
 */
export class FastTrackActivity {
  private readonly announcer = inject(LiveAnnouncer);

  model = signal<FastTrackActivityModel>({
    title: "",
    contact: [""],
    startDate: null,
    endDate: null,
    keywords: { german: [], english: [] },
  });

  activityForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
    required(schema.startDate, { message: "Start date is required" });
    validate(schema.startDate, (ctx) => {
      const value = ctx.value();

      if (value === null) {
        return void 0;
      }

      if (!(value instanceof Date) || Number.isNaN(value.getTime())) {
        return {
          kind: "invalidDate",
          message: "Must be a valid date",
        };
      }

      return void 0;
    });
    validate(schema.endDate, (ctx) => {
      const value = ctx.value();

      if (value === null) {
        return void 0;
      }

      if (!(value instanceof Date) || Number.isNaN(value.getTime())) {
        return {
          kind: "invalidDate",
          message: "Must be a valid date",
        };
      }

      return void 0;
    });
    minDate(schema.endDate, (ctx) => ctx.stateOf(schema.startDate).value() ?? undefined, {
      message: "End date must be on or after start date",
    });
  });

  addKeyword(event: MatChipInputEvent, language: "german" | "english"): void {
    const value = (event.value || "").trim();

    if (value) {
      this.model.update((current) => {
        const keywords = {
          ...current.keywords,
          [language]: [...current.keywords[language], value],
        };
        return { ...current, keywords };
      });
    }

    event.chipInput?.clear();
  }

  removeKeyword(keyword: string, language: "german" | "english"): void {
    const keywords = this.model().keywords[language];
    const index = keywords.lastIndexOf(keyword);

    if (index > -1) {
      const nextKeywords = [...keywords.slice(0, index), ...keywords.slice(index + 1)];
      this.model.update((current) => ({
        ...current,
        keywords: { ...current.keywords, [language]: nextKeywords },
      }));
      this.announcer.announce(`removed ${keyword} from reactive form`);
    }
  }
  onSubmit() {
    // eslint-disable-next-line no-console
    console.log("Submitted", this.model());
  }
}
