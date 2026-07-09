import { Component, Input, input, model } from "@angular/core";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatSelectModule } from "@angular/material/select";
import type { FormValueControl } from "@angular/forms/signals";
import type { Mitarbeiter } from "../models/project.model";

@Component({
  selector: "app-employee-multiselect",
  standalone: true,
  imports: [MatFormFieldModule, MatSelectModule],
  template: `
    <mat-form-field appearance="outline" class="employee-field">
      <mat-label>Employees</mat-label>
      <mat-select multiple [value]="value()" (selectionChange)="value.set($event.value)" [disabled]="disabled()">
        @for (employee of options; track employee.id) {
          <mat-option [value]="employee.id">
            {{ employee.vorname }} {{ employee.nachname }}
          </mat-option>
        }
      </mat-select>
    </mat-form-field>
  `,
  styles: [
    `
      .employee-field {
        width: 100%;
      }
    `,
  ],
})
export class EmployeeMultiSelectComponent implements FormValueControl<string[]> {
  readonly value = model<string[]>([]);
  readonly disabled = input(false);

  @Input() options: readonly Mitarbeiter[] = [];
}
