import { Component, inject } from "@angular/core";
import { ActivatedRoute, RouterLink, RouterOutlet } from "@angular/router";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatListModule } from "@angular/material/list";
import { MatButtonModule } from "@angular/material/button";
import type { Project } from "../models/project.model";
import { DummyDataService } from "../services/dummy-data.service";
import { AuthService } from "../auth";

@Component({
  selector: "app-project-detail",
  standalone: true,
  imports: [CommonModule, MatCardModule, MatListModule, MatButtonModule, RouterLink, RouterOutlet],
  template: `
    <div class="page-project-detail">
      <div class="project-main">
        @if (project) {
          <mat-card>
            <mat-card-header>
              <div mat-card-avatar class="project-icon">📋</div>
              <mat-card-title>{{ project.name }}</mat-card-title>
              <mat-card-subtitle>
                {{ project.startdatum | date: "dd.MM.yyyy" }} -
                {{ project.enddatum | date: "dd.MM.yyyy" }}
              </mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <p>{{ project.beschreibung }}</p>
            </mat-card-content>
            <mat-card-actions align="end">
              @if (authService.isLoggedIn()) {
                <button mat-raised-button color="primary" [routerLink]="['/edit', project.id]">
                  Edit Project
                </button>
              }
            </mat-card-actions>
          </mat-card>

          <mat-card>
            <mat-card-title>Mitarbeiter ({{ project.mitarbeiter.length }})</mat-card-title>
            <mat-list>
              @for (m of project.mitarbeiter; track m.id) {
                <a
                  mat-list-item
                  [routerLink]="['/projekte', project.id, 'mitarbeiter', m.id]"
                  class="mitarbeiter-link"
                >
                  <span matListItemTitle>{{ m.vorname }} {{ m.nachname }}</span>
                  <span matListItemLine>Geb.: {{ m.geburtsdatum | date: "dd.MM.yyyy" }}</span>
                </a>
              }
            </mat-list>
          </mat-card>
        } @else {
          <p>Project not found</p>
        }
      </div>

      <div class="project-detail">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: `
    .page-project-detail {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      padding: 20px;
    }

    .project-main {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    mat-card {
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    mat-card-header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;
    }

    .project-icon {
      font-size: 32px;
      width: auto;
      height: auto;
    }

    .mitarbeiter-link {
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: #f5f5f5;
      }
    }

    @media (max-width: 768px) {
      .page-project-detail {
        grid-template-columns: 1fr;
      }
    }
  `,
})
export class ProjectDetailComponent {
  private route = inject(ActivatedRoute);
  private dummyDataService = inject(DummyDataService);
  authService = inject(AuthService);

  project: Project | undefined;

  constructor() {
    this.route.params.subscribe((params) => {
      this.project = this.dummyDataService.getProjectById(params["id"]);
    });
  }
}
