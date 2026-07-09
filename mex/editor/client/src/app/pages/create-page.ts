import { Component, ViewChild, inject } from "@angular/core";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { CommonModule } from "@angular/common";
import { AuthService } from "../auth";
import { DummyDataService } from "../services/dummy-data.service";
import type { Project, Mitarbeiter } from "../models/project.model";
import { ProjectFormComponent } from "../components/project-form.component";
import { createEmptyProjectFormValue, selectedMitarbeiterFromIds, type ProjectFormValue } from "../models/project-form.model";

@Component({
	selector: "app-create-page",
	standalone: true,
	imports: [
		CommonModule,
		ProjectFormComponent,
		MatIconModule,
		MatSnackBarModule,
	],
	template: `
		<main class="main">
			<h1>Create Project</h1>
      @if (authService.isLoggedIn()) {
        <app-project-form
          #projectFormComponent
          title="New Project"
          submitLabel="Create"
          secondaryLabel="Reset"
          secondaryAction="reset"
          [availableMitarbeiter]="availableMitarbeiter"
          [initialValue]="initialProjectValue"
          (save)="onSubmit($event)"
        ></app-project-form>
      }
      @else {
        <p>Please log in to create items.</p>
        <mat-icon aria-hidden="false" fontIcon="lock"></mat-icon>
      }
		</main>
	`,
	styles: [
		`
			.main {
				padding: 2.5rem 3rem;
			}

      .create-form {
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

      .lock-card {
        background: rgba(252, 252, 252, 0.8);
        border: 1px solid rgba(245, 133, 91, 0.2);
        max-width: 400px;
        text-align: center;
      }

      .lock-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: rgb(122, 174, 218);
        margin-bottom: 1rem;
      }

      textarea {
        font-family: inherit;
        resize: vertical;
      }
		`,
	],
})
export class CreatePageComponent {
  @ViewChild("projectFormComponent") private projectFormComponent?: ProjectFormComponent;

	authService = inject(AuthService);
	private dummyDataService = inject(DummyDataService);
	private snackBar = inject(MatSnackBar);

  initialProjectValue = createEmptyProjectFormValue();
	availableMitarbeiter: Mitarbeiter[] = [];

	constructor() {
		// Load available employees from dummy data
		this.availableMitarbeiter = this.dummyDataService.getAvailableMitarbeiter();
	}

  onSubmit(formValue: ProjectFormValue): void {
    const newProject: Project = {
      id: "p" + Date.now(),
      name: formValue.name,
      beschreibung: formValue.beschreibung,
      startdatum: new Date(formValue.startdatum ?? new Date()),
      enddatum: new Date(formValue.enddatum ?? new Date()),
      mitarbeiter: selectedMitarbeiterFromIds(formValue.mitarbeiterIds, this.availableMitarbeiter),
    };

    // Save project to dummy data service
    this.dummyDataService.addProject(newProject);

    this.snackBar.open(`Projekt "${newProject.name}" erfolgreich erstellt!`, "Schließen", {
      duration: 3000,
      horizontalPosition: "end",
      verticalPosition: "top",
    });

    this.projectFormComponent?.resetToInitial();
	}
}
