import { Component, inject } from "@angular/core";
import type { OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
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
import { ProjectFormComponent } from "../components/project-form.component";
import { projectToFormValue, selectedMitarbeiterFromIds, type ProjectFormValue } from "../models/project-form.model";

@Component({
  selector: "app-edit-page",
  standalone: true,
  imports: [
    CommonModule,
    ProjectFormComponent,
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
        @if (projectFormValue) {
          <app-project-form
            title="Edit Project"
            submitLabel="Save Changes"
            secondaryLabel="Cancel"
            secondaryAction="cancel"
            [availableMitarbeiter]="availableMitarbeiter"
            [initialValue]="projectFormValue"
            (save)="onSubmit($event)"
            (secondary)="onCancel()"
          ></app-project-form>
        }
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
  private snackBar = inject(MatSnackBar);

  project: Project | undefined;
  projectFormValue: ProjectFormValue | undefined;
  availableMitarbeiter: Mitarbeiter[] = [];
  projectId = "";

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.projectId = params["id"];
      this.project = this.dummyDataService.getProjectById(this.projectId);

      if (this.project) {
        this.projectFormValue = projectToFormValue(this.project);
      }
    });

    this.availableMitarbeiter = this.dummyDataService.getAvailableMitarbeiter();
  }

  onSubmit(formValue: ProjectFormValue): void {
    if (!this.project) {
      return;
    }

    const updatedProject: Project = {
      ...this.project,
      name: formValue.name,
      beschreibung: formValue.beschreibung,
      startdatum: new Date(formValue.startdatum ?? new Date()),
      enddatum: new Date(formValue.enddatum ?? new Date()),
      mitarbeiter: selectedMitarbeiterFromIds(formValue.mitarbeiterIds, this.availableMitarbeiter),
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

  onCancel(): void {
    this.router.navigate(["/projekte", this.projectId]);
  }
}
