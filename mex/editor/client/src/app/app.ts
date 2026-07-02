import { Component, ChangeDetectionStrategy } from "@angular/core";
import { MatIcon } from "@angular/material/icon";
import { RouterOutlet } from "@angular/router";
import { NavBarComponent } from "./components/nav-bar-component/nav-bar-component";

@Component({
  selector: "app-root",
  imports: [RouterOutlet, MatIcon, NavBarComponent],
  templateUrl: "./app.html",
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: "./app.scss",
})
export class App {}
