import { Component, inject } from "@angular/core";
import type { FormGroup} from "@angular/forms";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MatSelectModule } from "@angular/material/select";
import { MatCardModule } from "@angular/material/card";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { CommonModule } from "@angular/common";
import { AuthService } from "../auth";
import { DummyDataService } from "../services/dummy-data.service";
import type { Project, Mitarbeiter } from "../models/project.model";

@Component({
	selector: "app-create-page",
	standalone: true,
	imports: [
		CommonModule,
		ReactiveFormsModule,
		MatIconModule,
		MatButtonModule,
		MatFormFieldModule,
		MatInputModule,
		MatDatepickerModule,
		MatNativeDateModule,
		MatSelectModule,
		MatCardModule,
		MatSnackBarModule,
	],
	template: `
		<main class="main">
			<h1>Create Project</h1>
      @if (authService.isLoggedIn()) {
        <form [formGroup]="projectForm" (ngSubmit)="onSubmit()" class="create-form">
          <mat-card>
            <mat-card-title>New Project</mat-card-title>
            <mat-card-content>
              <!-- Project Name -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Project Name</mat-label>
                <input matInput formControlName="name" placeholder="e.g., MEx Editor" />
                @if (projectForm.get('name')?.hasError('required')) {
                  <mat-error>Project name is required</mat-error>
                }
              </mat-form-field>

              <!-- Description -->
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Description</mat-label>
                <textarea matInput formControlName="beschreibung" placeholder="Project description" rows="4"></textarea>
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
              <button mat-button type="button" (click)="onReset()">Reset</button>
              <button mat-flat-button color="primary" type="submit" [disabled]="projectForm.invalid">
                Create
              </button>
            </mat-card-actions>
          </mat-card>
        </form>
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
	authService = inject(AuthService);
	private dummyDataService = inject(DummyDataService);
	private fb = inject(FormBuilder);
	private snackBar = inject(MatSnackBar);

	projectForm: FormGroup;
	availableMitarbeiter: Mitarbeiter[] = [];

	constructor() {
		this.projectForm = this.fb.group({
			name: ["", [Validators.required, Validators.minLength(3)]],
			beschreibung: ["", [Validators.required, Validators.minLength(5)]],
			startdatum: ["", Validators.required],
			enddatum: ["", Validators.required],
			mitarbeiter: [[]],
		});

		// Load available employees from dummy data
		this.availableMitarbeiter = this.dummyDataService.getAvailableMitarbeiter();
	}

	onSubmit(): void {
		if (this.projectForm.valid) {
			const newProject: Project = {
				id: "p" + Date.now(),
				name: this.projectForm.get("name")?.value,
				beschreibung: this.projectForm.get("beschreibung")?.value,
				startdatum: new Date(this.projectForm.get("startdatum")?.value),
				enddatum: new Date(this.projectForm.get("enddatum")?.value),
				mitarbeiter: this.projectForm.get("mitarbeiter")?.value || [],
			};

			// Save project to dummy data service
			this.dummyDataService.addProject(newProject);

			this.snackBar.open(`Projekt "${newProject.name}" erfolgreich erstellt!`, "Schließen", {
				duration: 3000,
				horizontalPosition: "end",
				verticalPosition: "top",
			});

			this.projectForm.reset();
		}
	}

	onReset(): void {
		this.projectForm.reset();
	}
}
