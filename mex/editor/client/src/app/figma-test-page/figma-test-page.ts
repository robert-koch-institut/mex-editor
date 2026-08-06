import { Component, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatButton, MatMiniFabButton } from "@angular/material/button";
import { MatButtonToggleModule } from "@angular/material/button-toggle";
import { MatCheckbox } from "@angular/material/checkbox";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIcon } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { TextFieldModule } from "@angular/cdk/text-field";

@Component({
  selector: "mex-figma-test-page",
  imports: [
    FormsModule,
    MatButton,
    MatMiniFabButton,
    MatButtonToggleModule,
    MatIcon,
    MatSelectModule,
    MatCheckbox,
    MatSlideToggleModule,
    MatFormFieldModule,
    MatInputModule,
    TextFieldModule,
  ],
  templateUrl: "./figma-test-page.html",
  styleUrl: "./figma-test-page.scss",
})
/**
 * FigmaTestPage for the app.
 */
export class FigmaTestPage {
  description = signal("");
  value = signal<number | null>(null);
  options = [
    { label: "None", value: null },
    { label: "One", value: 1 },
    { label: "Two", value: 2 },
    { label: "Three", value: 3 },
  ];
}
