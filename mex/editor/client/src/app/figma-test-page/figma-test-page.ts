import { Component } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MatButtonToggle, MatButtonToggleGroup } from "@angular/material/button-toggle";
import { MatCheckbox } from "@angular/material/checkbox";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIcon } from "@angular/material/icon";
import { MatHint, MatInput } from "@angular/material/input";
import { MatLabel, MatOption, MatSelect } from "@angular/material/select";
import { MatSlideToggle } from "@angular/material/slide-toggle";

@Component({
  selector: "mex-figma-test-page",
  imports: [
    MatButtonModule,
    MatButtonToggle,
    MatButtonToggleGroup,
    MatCheckbox,
    MatDatepickerModule,
    MatFormFieldModule,
    MatHint,
    MatIcon,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    MatSlideToggle,
  ],
  templateUrl: "./figma-test-page.html",
  styleUrl: "./figma-test-page.scss",
})
/**
 * Page to visually check if all material components look as rki as possbile.
 */
export class FigmaTestPage {}
