import { Component, EventEmitter, input, Input, Output } from "@angular/core";
import { signal } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatNativeDateModule } from "@angular/material/core";
import { FormField, FormRoot, form, minLength, required } from "@angular/forms/signals";
import type { Mitarbeiter } from "../models/project.model";
import {
  createEmptyProjectFormValue,
  type ProjectFormValue,
} from "../models/project-form.model";
import { EmployeeMultiSelectComponent } from "./employee-multiselect.component";

@Component({
  selector: "app-project-form",
  standalone: true,
  imports: [
    FormField,
    FormRoot,
    MatButtonModule,
    MatCardModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    MatNativeDateModule,
    EmployeeMultiSelectComponent,
  ],
  template: `
    <form class="project-form" [formRoot]="projectForm" (submit)="submitForm($event)">
      <mat-card>
        <mat-card-title>{{ title() }}</mat-card-title>
        <mat-card-content>
          <div class="form-grid">
          <mat-form-field appearance="outline" class="form-field">
            <mat-label>Project Name</mat-label>
            <input matInput [formField]="projectForm.name" placeholder="e.g., MEx Editor" />
            @for (error of projectForm.name().errors(); track error) {
                <mat-error>{{ error.message }}</mat-error>
            }
          </mat-form-field>

          <mat-form-field appearance="outline" class="form-field">
            <mat-label>Description</mat-label>
            <textarea
              matInput
              [formField]="projectForm.beschreibung"
              placeholder="Project description"
              rows="4"
            ></textarea>
            @for (error of projectForm.beschreibung().errors(); track error) {
              <mat-error>{{ error.message }}</mat-error>
            }
          </mat-form-field>

          <mat-form-field appearance="outline" class="form-field">
            <mat-label>Start Date</mat-label>
            <input matInput [matDatepicker]="startPicker" [formField]="projectForm.startdatum" />
            <mat-datepicker-toggle matIconSuffix [for]="startPicker"></mat-datepicker-toggle>
            <mat-datepicker #startPicker></mat-datepicker>
            @for (error of projectForm.startdatum().errors(); track error) {
              <mat-error>{{ error.message }}</mat-error>
            }
          </mat-form-field>

          <mat-form-field appearance="outline" class="form-field">
            <mat-label>End Date</mat-label>
            <input matInput [matDatepicker]="endPicker" [formField]="projectForm.enddatum" />
            <mat-datepicker-toggle matIconSuffix [for]="endPicker"></mat-datepicker-toggle>
            <mat-datepicker #endPicker></mat-datepicker>
            @for (error of projectForm.enddatum().errors(); track error) {
              <mat-error>{{ error.message }}</mat-error>
            }
          </mat-form-field>

          <app-employee-multiselect
            class="form-field"
            [formField]="projectForm.mitarbeiterIds"
            [options]="availableMitarbeiter"
          />
          </div>
        </mat-card-content>

        <mat-card-actions align="end">
          <button mat-button type="button" (click)="handleSecondaryAction()">{{ secondaryLabel() }}</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="projectForm().invalid()">
            {{ submitLabel() }}
          </button>
        </mat-card-actions>
      </mat-card>
    </form>
  `,
  styles: [
    `
      .project-form {
        max-width: 600px;
        margin: 0 auto;
      }

      .form-grid {
        display: grid;
        gap: 1rem;
      }

      .form-field {
        width: 100%;
        margin-bottom: 1rem;
      }

      :host ::ng-deep .mat-mdc-form-field {
        width: 100%;
      }

      :host ::ng-deep .mat-mdc-form-field .mat-mdc-floating-label {
        color: var(--text);
      }

      :host ::ng-deep .mat-mdc-text-field-wrapper {
        background: rgba(233, 236, 250, 0.9);
      }

      mat-card {
        background: rgba(252, 252, 252, 0.8);
        border: 1px solid rgba(91, 138, 245, 0.2);
        padding: 1.5rem;
      }

      mat-card-title {
        font-size: 1rem;
        margin-bottom: 1.5rem;
        color: var(--accent2);
      }

      mat-card-actions {
        padding-top: 1.5rem;
        gap: 1rem;
      }

      mat-error {
        font-size: 0.8rem;
      }

      textarea {
        font-family: inherit;
        resize: vertical;
      }
    `,
  ],
})
export class ProjectFormComponent {
  title = input("New Project");
  submitLabel = input("Submit");
  secondaryLabel = input("Reset");
  secondaryAction = input<"reset" | "cancel">("reset");
  @Input() availableMitarbeiter: readonly Mitarbeiter[] = [];

  @Input()
  set initialValue(value: ProjectFormValue | null | undefined) {
    this.initialProjectValue = value ?? createEmptyProjectFormValue();
    this.projectModel.set(this.initialProjectValue);
  }

  @Output() save = new EventEmitter<ProjectFormValue>();
  @Output() secondary = new EventEmitter<void>();

  private initialProjectValue = createEmptyProjectFormValue();
  private projectModel = signal<ProjectFormValue>(createEmptyProjectFormValue());

  projectForm = form(this.projectModel, (schema) => {
    required(schema.name, { message: "Project name is required" });
    minLength(schema.name, 3, { message: "Project name must be at least 3 characters" });
    required(schema.beschreibung, { message: "Description is required" });
    minLength(schema.beschreibung, 5, { message: "Description must be at least 5 characters" });
    required(schema.startdatum, { message: "Start date is required" });
    required(schema.enddatum, { message: "End date is required" });
  });

  submitForm(event: SubmitEvent): void {
    event.preventDefault();
    this.save.emit(this.projectModel());
  }

  handleSecondaryAction(): void {
    if (this.secondaryAction() === "cancel") {
      this.secondary.emit();
      return;
    }

    this.resetToInitial();
  }

  resetToInitial(): void {
    this.projectModel.set({ ...this.initialProjectValue, mitarbeiterIds: [...this.initialProjectValue.mitarbeiterIds] });
  }
}
