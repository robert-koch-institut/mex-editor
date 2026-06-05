import { Component, inject } from "@angular/core";
import type { OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import type { FormGroup } from "@angular/forms";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatSelectModule } from "@angular/material/select";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { type Project, type Mitarbeiter } from "../models/project.model";
import { DummyDataService } from "../services/dummy-data.service";

@Component({
  selector: "app-edit-page",
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSelectModule,
    MatSnackBarModule,
  ],
  template: `
    <main class="main">
      <h1>Edit Project</h1>
      @if (project) {
        <form [formGroup]="projectForm" (ngSubmit)="onSubmit()" class="edit-form">
          <mat-card>
            <mat-card-title>{{ project.name }}</mat-card-title>
            <mat-card-content>
              <!-- Project Name -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Project Name</mat-label>
                <input matInput formControlName="name" />
                @if (projectForm.get('name')?.hasError('required')) {
                  <mat-error>Project name is required</mat-error>
                }
              </mat-form-field>

              <!-- Description -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Description</mat-label>
                <textarea matInput formControlName="beschreibung" rows="4"></textarea>
                @if (projectForm.get('beschreibung')?.hasError('required')) {
                  <mat-error>Description is required</mat-error>
                }
              </mat-form-field>

              <!-- Start Date -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Start Date</mat-label>
                <input matInput [matDatepicker]="startPicker" formControlName="startdatum" />
                <mat-datepicker-toggle matIconSuffix [for]="startPicker"></mat-datepicker-toggle>
                <mat-datepicker #startPicker></mat-datepicker>
                @if (projectForm.get('startdatum')?.hasError('required')) {
                  <mat-error>Start date is required</mat-error>
                }
              </mat-form-field>

              <!-- End Date -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>End Date</mat-label>
                <input matInput [matDatepicker]="endPicker" formControlName="enddatum" />
                <mat-datepicker-toggle matIconSuffix [for]="endPicker"></mat-datepicker-toggle>
                <mat-datepicker #endPicker></mat-datepicker>
                @if (projectForm.get('enddatum')?.hasError('required')) {
                  <mat-error>End date is required</mat-error>
                }
              </mat-form-field>

              <!-- Employees Selection -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Employees</mat-label>
                <mat-select formControlName="mitarbeiter" multiple>
                  @for (emp of availableMitarbeiter; track emp.id) {
                    <mat-option [value]="emp">
                      {{ emp.vorname }} {{ emp.nachname }}
                    </mat-option>
                  }
                </mat-select>
              </mat-form-field>
            </mat-card-content>

            <mat-card-actions align="end">
              <button mat-button type="button" (click)="onCancel()">Cancel</button>
              <button mat-flat-button color="primary" type="submit" [disabled]="projectForm.invalid">
                Save Changes
              </button>
            </mat-card-actions>
          </mat-card>
        </form>
      } @else {
        <p>Please select a project from the search tab to edit.</p>
      }
    </main>
  `,
  styles: [
    `
      .main {
        padding: 2.5rem 3rem;
      }

      .edit-form {
        max-width: 600px;
        margin: 0 auto;
      }

      .form-field {
        width: 100%;
        margin-bottom: 1rem;
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

      textarea {
        font-family: inherit;
        resize: vertical;
      }

      .info-card {
        background: rgba(252, 252, 252, 0.8);
        border: 1px solid rgba(56, 232, 197, 0.3);
        padding: 2rem;
        max-width: 500px;
        margin: 2rem auto;
      }

      .info-card p {
        text-align: center;
        font-size: 1.1rem;
        color: var(--text);
      }
    `,
  ],
})
export class EditPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private dummyDataService = inject(DummyDataService);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  projectForm: FormGroup;
  project: Project | undefined;
  availableMitarbeiter: Mitarbeiter[] = [];
  projectId = "";

  constructor() {
    this.projectForm = this.fb.group({
      name: ["", [Validators.required, Validators.minLength(3)]],
      beschreibung: ["", [Validators.required, Validators.minLength(5)]],
      startdatum: ["", Validators.required],
      enddatum: ["", Validators.required],
      mitarbeiter: [[]],
    });
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.projectId = params["id"];
      this.project = this.dummyDataService.getProjectById(this.projectId);

      if (this.project) {
        // Pre-populate form with project data
        this.projectForm.patchValue({
          name: this.project.name,
          beschreibung: this.project.beschreibung,
          startdatum: this.project.startdatum,
          enddatum: this.project.enddatum,
          mitarbeiter: this.project.mitarbeiter,
        });
      }
    });

    this.availableMitarbeiter = this.dummyDataService.getAvailableMitarbeiter();
  }

  onSubmit(): void {
    if (this.projectForm.valid && this.project) {
      const updatedProject: Project = {
        ...this.project,
        name: this.projectForm.get("name")?.value,
        beschreibung: this.projectForm.get("beschreibung")?.value,
        startdatum: new Date(this.projectForm.get("startdatum")?.value),
        enddatum: new Date(this.projectForm.get("enddatum")?.value),
        mitarbeiter: this.projectForm.get("mitarbeiter")?.value || [],
      };

      // Update project in dummy data service
      this.dummyDataService.updateProject(updatedProject);

      this.snackBar.open(`Project "${updatedProject.name}" updated successfully!`, "Close", {
        duration: 3000,
        horizontalPosition: "end",
        verticalPosition: "top",
      });

      // Navigate back to project detail
      this.router.navigate(["/projekte", this.projectId]);
    }
  }

  onCancel(): void {
    this.router.navigate(["/projekte", this.projectId]);
  }
}
