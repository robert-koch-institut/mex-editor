import { Component, inject } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { CommonModule } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatIconModule } from "@angular/material/icon";
import type { Mitarbeiter } from "../models/project.model";
import { DummyDataService } from "../services/dummy-data.service";

@Component({
  selector: "app-mitarbeiter-detail",
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  template: `
    <div class="mitarbeiter-detail">
      @if (mitarbeiter) {
        <mat-card>
          <mat-card-header>
            <div mat-card-avatar class="avatar">👤</div>
            <mat-card-title>{{ mitarbeiter.vorname }} {{ mitarbeiter.nachname }}</mat-card-title>
            <mat-card-subtitle>Mitarbeiter-Details</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="detail-row">
              <span class="label">Vorname:</span>
              <span class="value">{{ mitarbeiter.vorname }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Nachname:</span>
              <span class="value">{{ mitarbeiter.nachname }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Geburtsdatum:</span>
              <span class="value">{{ mitarbeiter.geburtsdatum | date: "dd.MM.yyyy" }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Alter:</span>
              <span class="value">{{ getAlter(mitarbeiter.geburtsdatum) }} Jahre</span>
            </div>
          </mat-card-content>
        </mat-card>
      } @else {
        <mat-card>
          <mat-card-content>
            <p><mat-icon>error</mat-icon> Mitarbeiter nicht gefunden</p>
          </mat-card-content>
        </mat-card>
      }
    </div>
  `,
  styles: `
    .mitarbeiter-detail {
      padding: 20px;
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

    .avatar {
      font-size: 40px;
      width: auto;
      height: auto;
    }

    .detail-row {
      display: grid;
      grid-template-columns: 120px 1fr;
      gap: 16px;
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid #eee;

      &:last-child {
        border-bottom: none;
      }
    }

    .label {
      font-weight: 600;
      color: #666;
    }

    .value {
      color: #333;
    }

    mat-icon {
      vertical-align: middle;
      margin-right: 8px;
    }
  `,
})
export class MitarbeiterDetailComponent {
  private route = inject(ActivatedRoute);
  private dummyDataService = inject(DummyDataService);

  mitarbeiter: Mitarbeiter | undefined;

  constructor() {
    this.route.params.subscribe((params) => {
      this.mitarbeiter = this.dummyDataService.getMitarbeiterById(params["mid"]);
    });
  }

  getAlter(geburtsdatum: Date): number {
    const today = new Date();
    const birthDate = new Date(geburtsdatum);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }
}
