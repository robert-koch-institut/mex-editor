import { LiveAnnouncer } from "@angular/cdk/a11y";
import { Component, inject, signal } from "@angular/core";
import { form, minDate, minLength, required, validate, FormField } from "@angular/forms/signals";
import { MatNativeDateModule } from "@angular/material/core";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormField, MatLabel, MatError, MatHint } from "@angular/material/select";
import { MatInput } from "@angular/material/input";
import { MatButton } from "@angular/material/button";
import { MatChipsModule } from "@angular/material/chips";
import type { MatChipInputEvent } from "@angular/material/chips";
import { MatIconModule } from "@angular/material/icon";
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';

interface CreateContactPointModel {
  $type: "CreateContactPointModel";
  email: string;
}
interface CreatePersonModel {
  $type: "CreatePersonModel";
  firstname: number;
  lastname: number;
}
type CreateContactModel = CreateContactPointModel | CreatePersonModel;
interface FastTrackActivityModel {
  title: string;
  contact: (string | CreateContactModel)[];
  startDate: Date | null;
  endDate: Date | null;
  keywords: KeywordDict;
}
interface KeywordDict {
  german: string[];
  english: string[];
}

@Component({
  selector: "mex-fast-track-activity",
  imports: [
    MatButton,
    FormField,
    MatFormField,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatLabel,
    MatError,
    MatInput,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatHint,
    MatChipsModule,
    MatIconModule,
  ],
  templateUrl: "./fast-track-activity.html",
  styleUrl: "./fast-track-activity.scss",
})
export class FastTrackActivity {
  private readonly announcer = inject(LiveAnnouncer);

  model = signal<FastTrackActivityModel>({
    title: "",
    contact: [""],
    startDate: null,
    endDate: null,
    keywords: { german: [], english: [] }
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

  addKeyword(event: MatChipInputEvent, language: 'german' | 'english'): void {
    const value = (event.value || "").trim();

    if (value) {
      this.model.update(
        (current) => {
          const keywords = {...current.keywords, [language]: [...current.keywords[language], value] };
          return {...current, keywords}}
      )
    }

    event.chipInput?.clear();
  }

  removeKeyword(keyword: string, language: 'german' | 'english'): void {
    const keywords = this.model().keywords[language];
    const index = keywords.lastIndexOf(keyword);

    if (index > -1) {
      const nextKeywords = [...keywords.slice(0, index), ...keywords.slice(index + 1)];
      this.model.update((current) => ({
        ...current,
        keywords: { ...current.keywords, [language]: nextKeywords }
      }));
      this.announcer.announce(`removed ${keyword} from reactive form`);
    }
  }

  onSubmit($event: SubmitEvent) {
    console.warn("Submitted", $event, this.model());
  }
}
